"""Smoke tests for the FedMed core modules."""

from __future__ import annotations

import numpy as np
import torch

from fedmed.config import CONFIG
from fedmed.data import load_global_validation, load_pooled_training_set
from fedmed.metrics import dice_score, evaluate_model
from fedmed.model import build_model, count_parameters
from fedmed.privacy import dp as dp_mod
from fedmed.privacy import he as he_mod


def test_model_forward() -> None:
    model = build_model()
    print(f"  params: {count_parameters(model):,}")
    x = torch.randn(1, 1, *CONFIG.model.spatial_size)
    with torch.no_grad():
        y = model(x)
    assert y.shape == (1, CONFIG.model.out_channels, *CONFIG.model.spatial_size), y.shape
    print(f"  forward OK -> {tuple(y.shape)}")


def test_dataset_and_metrics() -> None:
    images, labels = load_pooled_training_set()
    val_images, val_labels = load_global_validation()
    print(f"  pooled train: {tuple(images.shape)}")
    print(f"  pooled val:   {tuple(val_images.shape)}")

    model = build_model()
    from torch.utils.data import DataLoader, TensorDataset

    loader = DataLoader(
        TensorDataset(val_images[:4], val_labels[:4]), batch_size=2, shuffle=False
    )
    metrics = evaluate_model(model, loader, CONFIG.model.num_classes)
    print(f"  untrained metrics: {metrics}")

    mean, per_class = dice_score(labels[:4], labels[:4], CONFIG.model.num_classes)
    assert mean > 99.0, f"perfect prediction should score ~100, got {mean}"
    print(f"  perfect-prediction dice: {mean:.2f}% per_class={per_class}")


def test_he_roundtrip() -> None:
    session = he_mod.create_session("test-node")
    if not session.available:
        print("  TenSEAL unavailable - skipping")
        return

    model = build_model()
    state = {k: v.detach().cpu() for k, v in model.state_dict().items()}

    blob = he_mod.encrypt_state_dict(session, state)
    print(f"  ciphertext size: {he_mod.blob_size(blob):,} bytes")
    print(f"  plaintext size:  {sum(v.numel() for v in state.values()):,} floats")

    restored = he_mod.decrypt_state_dict(session, blob, state)
    max_err = max(
        float((restored[k].to(torch.float64) - v.to(torch.float64)).abs().max())
        for k, v in state.items()
    )
    print(f"  max decryption error: {max_err:.2e}")
    assert max_err < 1e-2, max_err

    b1 = he_mod.encrypt_state_dict(session, state)
    b2 = he_mod.encrypt_state_dict(session, state)
    summed = session.decrypt_sum([b1, b2])
    plain_sum = he_mod.tensor_to_flat_vector(state) * 2
    err = float(np.abs(summed - plain_sum).max())
    print(f"  homomorphic-sum max error: {err:.2e}")
    assert err < 1e-2, err


def test_dp() -> None:
    model = build_model()
    state = {k: v.detach().cpu() for k, v in model.state_dict().items()}

    # Build a fake per-patient gradient batch from the model's parameters.
    grads = []
    for i in range(4):
        torch.manual_seed(i)
        grads.append(
            torch.cat([torch.randn_like(p.float()).reshape(-1) for p in model.parameters()])
        )

    noised, stats = dp_mod.add_gaussian_noise_to_gradients(grads, 0.5, 1.0)
    print(f"  dp stats: {stats}")
    assert stats["noise_l2_norm"] > 0
    assert stats["patients_protected"] == 4
    assert torch.isfinite(noised).all()

    acct = dp_mod.DPAccountant(participation_ratio=0.67)
    acct.spend(10)
    print(f"  epsilon after 10 rounds: {acct.epsilon}")
    assert acct.epsilon > 0


def main() -> None:
    print("\n=== MODEL ===")
    test_model_forward()
    print("\n=== DATA + METRICS ===")
    test_dataset_and_metrics()
    print("\n=== HOMOMORPHIC ENCRYPTION ===")
    test_he_roundtrip()
    print("\n=== DIFFERENTIAL PRIVACY ===")
    test_dp()
    print("\nAll core smoke tests passed.\n")


if __name__ == "__main__":
    main()
