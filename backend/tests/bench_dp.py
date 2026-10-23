"""Measure per-sample gradient norms to calibrate the DP clip bound."""

from __future__ import annotations

import time

import torch
from monai.networks.nets import UNet

from fedmed.data import build_local_loaders
from fedmed.metrics import dice_ce_loss


def main() -> None:
    torch.manual_seed(0)
    model = UNet(
        spatial_dims=3, in_channels=1, out_channels=3,
        channels=(16, 32, 64, 128), strides=(2, 2, 2), num_res_units=2,
        dropout=0.2, norm="INSTANCE", bias=True, up_kernel_size=3,
    )
    train_loader, _ = build_local_loaders("hospital-1", batch_size=2)

    norms = []
    t0 = time.time()
    for images, labels in train_loader:
        for i in range(images.shape[0]):
            model.zero_grad(set_to_none=True)
            logits = model(images[i : i + 1])
            loss = dice_ce_loss(logits, labels[i : i + 1], 3, ce_weight=0.5)
            loss.backward()
            g = torch.cat([
                p.grad.detach().reshape(-1)
                for p in model.parameters()
                if p.grad is not None
            ])
            norms.append(float(g.norm().item()))
    dt = time.time() - t0

    norms.sort()
    n = len(norms)
    print(f"samples measured : {n}")
    print(f"per-sample step  : {dt / max(n, 1):.3f}s")
    print(f"min  {norms[0]:.6e}")
    print(f"p25  {norms[n // 4]:.6e}")
    print(f"med  {norms[n // 2]:.6e}")
    print(f"p75  {norms[3 * n // 4]:.6e}")
    print(f"max  {norms[-1]:.6e}")
    print(f"mean {sum(norms) / n:.6e}")


if __name__ == "__main__":
    main()
