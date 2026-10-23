"""Quick training experiment: what Dice is achievable per model size?"""

from __future__ import annotations

import time

import torch
from monai.networks.nets import UNet
from torch.utils.data import DataLoader, TensorDataset

from fedmed.data import load_global_validation, load_pooled_training_set
from fedmed.metrics import dice_loss, evaluate_model


def train(model, loader, epochs, lr=1e-3):
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs * len(loader))
    model.train()
    for _ in range(epochs):
        for x, y in loader:
            opt.zero_grad()
            loss = dice_loss(model(x), y, 3)
            loss.backward()
            opt.step()
        sched.step()
    return model


def run(channels, res_units, epochs, lr=1e-3, tag=""):
    m = UNet(
        spatial_dims=3,
        in_channels=1,
        out_channels=3,
        channels=channels,
        strides=(2, 2, 2, 2)[: len(channels) - 1],
        num_res_units=res_units,
        dropout=0.1,
        norm="INSTANCE",
        bias=True,
        up_kernel_size=3,
    )
    params = sum(p.numel() for p in m.parameters())

    tr_x, tr_y = load_pooled_training_set()
    va_x, va_y = load_global_validation()
    tr = DataLoader(TensorDataset(tr_x, tr_y), batch_size=2, shuffle=True)
    va = DataLoader(TensorDataset(va_x, va_y), batch_size=2, shuffle=False)

    t = time.time()
    train(m, tr, epochs, lr)
    elapsed = time.time() - t
    met = evaluate_model(m, va, 3)
    print(
        f"{tag:22} ch={str(channels):18} res={res_units} params={params:>9,} "
        f"epochs={epochs} -> dice={met['dice']:6.2f}% loss={met['loss']:.4f} "
        f"acc={met['accuracy']:5.2f}% ({elapsed:.1f}s)"
    )
    return met["dice"]


if __name__ == "__main__":
    print()
    run((8, 16, 32, 64), 1, 6, tag="small")
    run((8, 16, 32, 64, 128), 1, 6, tag="medium")
    run((16, 32, 64, 128), 1, 6, tag="large")
    print()
