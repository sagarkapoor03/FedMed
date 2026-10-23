"""Diagnose convergence with the combined loss and tuned hyperparameters."""

from __future__ import annotations

import time

import torch
from monai.networks.nets import UNet
from torch.utils.data import DataLoader, TensorDataset

from fedmed.data import load_global_validation, load_pooled_training_set
from fedmed.metrics import dice_ce_loss, evaluate_model


def main():
    tr_x, tr_y = load_pooled_training_set()
    va_x, va_y = load_global_validation()
    tr = DataLoader(TensorDataset(tr_x, tr_y), batch_size=2, shuffle=True)
    va = DataLoader(TensorDataset(va_x, va_y), batch_size=2, shuffle=False)
    print(f"train={tr_x.shape} val={va_x.shape}")

    m = UNet(
        spatial_dims=3,
        in_channels=1,
        out_channels=3,
        channels=(16, 32, 64, 128),
        strides=(2, 2, 2, 2),
        num_res_units=1,
        dropout=0.1,
        norm="INSTANCE",
        bias=True,
        up_kernel_size=3,
    )
    opt = torch.optim.AdamW(m.parameters(), lr=1e-3, weight_decay=1e-4)
    epochs = 40
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs * len(tr))

    t = time.time()
    best = 0.0
    for ep in range(epochs):
        m.train()
        tot = 0.0
        for x, y in tr:
            opt.zero_grad()
            loss = dice_ce_loss(m(x), y, 3, ce_weight=0.5, dice_weight=1.0)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(m.parameters(), 5.0)
            opt.step()
            tot += loss.item()
        sched.step()
        if (ep + 1) % 4 == 0 or ep == 0:
            met = evaluate_model(m, va, 3)
            best = max(best, met["dice"])
            print(
                f"ep {ep + 1:3d} loss={tot / len(tr):.4f} "
                f"dice={met['dice']:6.2f}% per_class={met['per_class_dice']} "
                f"acc={met['accuracy']:.2f}% best={best:.2f}% ({time.time() - t:.0f}s)"
            )


if __name__ == "__main__":
    main()
