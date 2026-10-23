"""Fast in-process federated simulation used to calibrate the FL design.

Mirrors exactly what the Flower strategy does (FedAvg over the model
*delta*, per-node weighting, node dropout, per-sample DP-SGD) but runs in
a single process so a 10-round configuration can be evaluated in seconds
instead of minutes.

Usage:
    python -m tests.sim_fl --rounds 5 --dp per_sample --sigma 1.1
"""

from __future__ import annotations

import argparse
import time

import numpy as np
import torch
from monai.networks.nets import UNet

from fedmed.config import CONFIG
from fedmed.data import build_local_loaders, load_global_validation, make_loader
from fedmed.metrics import dice_ce_loss, evaluate_model
from fedmed.privacy.dp import add_gaussian_noise_to_gradients

MODELS = {
    "base": ((16, 32, 64, 128, 256), (2, 2, 2, 2), 2),
    "mid": ((16, 32, 64, 128), (2, 2, 2), 2),
    "small": ((16, 32, 64, 128), (2, 2, 2), 1),
    "tiny": ((8, 16, 32, 64), (2, 2, 2), 1),
}


def build(name: str) -> UNet:
    ch, st, ru = MODELS[name]
    return UNet(
        spatial_dims=3, in_channels=1, out_channels=3, channels=ch, strides=st,
        num_res_units=ru, dropout=0.2, norm="INSTANCE", bias=True, up_kernel_size=3,
    )


def local_train(
    model: UNet,
    loader,
    global_state: dict,
    epochs: int,
    lr: float,
    dp_mode: str,
    sigma_mult: float,
    clip: float,
    opt_name: str,
) -> tuple[dict, float, dict]:
    """Train locally and return (delta, local_loss, dp_stats)."""
    model.load_state_dict(global_state)
    if opt_name == "sgd":
        opt = torch.optim.SGD(model.parameters(), lr=lr, momentum=0.9)
    else:
        opt = torch.optim.AdamW(model.parameters(), lr=lr,
                                weight_decay=CONFIG.federated.weight_decay)

    model.train()
    running, steps = 0.0, 0
    dp_stats: dict = {}

    for _ in range(epochs):
        for images, labels in loader:
            if dp_mode == "per_sample":
                # DP-SGD: compute per-sample gradients, clip each, sum, add noise.
                params = [p for p in model.parameters() if p.requires_grad]
                grads = []
                for i in range(images.shape[0]):
                    model.zero_grad(set_to_none=True)
                    loss_i = dice_ce_loss(
                        model(images[i : i + 1]), labels[i : i + 1], 3, ce_weight=0.5
                    )
                    loss_i.backward()
                    grads.append(
                        torch.cat([
                            (p.grad.detach().reshape(-1) if p.grad is not None
                             else torch.zeros(p.numel()))
                            for p in params
                        ]).to(torch.float64)
                    )
                noised, dp_stats = add_gaussian_noise_to_gradients(
                    grads, sigma_mult, clip
                )
                # Scatter the noised summed gradient back into the params.
                offset = 0
                for p in params:
                    numel = p.numel()
                    p.grad = (
                        noised[offset : offset + numel]
                        .reshape(p.shape)
                        .to(p.dtype)
                        .clone()
                    )
                    offset += numel
                opt.step()
                running += float(noised.norm().item())
                steps += 1
                continue

            # Plain (non-private) training.
            opt.zero_grad()
            loss = dice_ce_loss(model(images), labels, 3, ce_weight=0.5)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            opt.step()
            running += loss.item()
            steps += 1

    new_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
    delta = {
        k: (new_state[k].to(torch.float64) - global_state[k].to(torch.float64))
        for k in new_state
    }
    return delta, running / max(steps, 1), dp_stats


def delta_norm(delta: dict) -> float:
    return float(
        np.sqrt(sum(float(v.pow(2).sum().item()) for v in delta.values()))
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=5)
    ap.add_argument("--model", type=str, default="small")
    ap.add_argument("--dp", type=str, default="none",
                    choices=["none", "per_sample", "update"])
    ap.add_argument("--sigma", type=float, default=1.1)
    ap.add_argument("--clip", type=float, default=1.0)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--opt", type=str, default="adamw", choices=["adamw", "sgd"])
    ap.add_argument("--dropout-round", type=int, default=0)
    args = ap.parse_args()

    torch.manual_seed(0)
    np.random.seed(0)

    model = build(args.model)
    nparams = sum(p.numel() for p in model.parameters())
    global_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

    loaders, sizes = {}, {}
    for h in CONFIG.hospitals:
        tr, _ = build_local_loaders(h.hospital_id, batch_size=args.batch)
        loaders[h.hospital_id] = tr
        sizes[h.hospital_id] = len(tr.dataset)

    val_x, val_y = load_global_validation()
    val_loader = make_loader(val_x, val_y, batch_size=4, shuffle=False)

    print(f"model={args.model} params={nparams:,} opt={args.opt} batch={args.batch} "
          f"epochs={args.epochs} lr={args.lr} dp={args.dp} sigma={args.sigma}")
    print(f"node sizes={sizes}  total train={sum(sizes.values())}")
    print()

    for rnd in range(1, args.rounds + 1):
        t0 = time.time()
        deltas, weights, norms = {}, {}, []
        active = list(loaders)
        if args.dropout_round and rnd == args.dropout_round:
            active = active[:-1]

        total = sum(sizes[h] for h in active)
        dp_agg = {}
        for h in active:
            d, local_loss, dp_stats = local_train(
                model, loaders[h], global_state, args.epochs, args.lr,
                args.dp, args.sigma, args.clip, args.opt,
            )
            deltas[h] = d
            weights[h] = sizes[h] / total
            norms.append(delta_norm(d))
            if dp_stats:
                dp_agg[h] = dp_stats

        agg = None
        for h in active:
            w = weights[h]
            contrib = {k: v * w for k, v in deltas[h].items()}
            agg = contrib if agg is None else {k: agg[k] + contrib[k] for k in agg}

        if args.dp == "update":
            # Clip the aggregate update and add isotropic Gaussian noise.
            n = float(np.sqrt(sum(float(v.pow(2).sum().item()) for v in agg.values())))
            d = sum(v.numel() for v in agg.values())
            if n > args.clip:
                sc = args.clip / (n + 1e-12)
                agg = {k: v * sc for k, v in agg.items()}
            std = args.sigma * args.clip / np.sqrt(d)
            for k in agg:
                agg[k] = agg[k] + torch.normal(
                    0.0, std, size=agg[k].shape, dtype=torch.float64
                )
            dp_agg = {"noise_l2_norm": round(float(std * np.sqrt(d)), 4),
                      "signal_l2_norm": round(n, 4),
                      "clip_norm": args.clip, "sigma": args.sigma}

        global_state = {
            k: (global_state[k].to(torch.float64) + agg[k]).to(dtype=global_state[k].dtype)
            for k in global_state
        }
        model.load_state_dict(global_state)

        m = evaluate_model(model, val_loader, 3)
        extra = ""
        if dp_agg:
            s = next(iter(dp_agg.values()))
            extra = f" snr={s.get('signal_to_noise', 0):.2f}"
        print(f"round {rnd:2d} dice={m['dice']:6.2f}% loss={m['loss']:.4f} "
              f"acc={m['accuracy']:.2f}% |d|={np.mean(norms):.4f}{extra} "
              f"{time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
