"""Benchmark model size / speed / HE ciphertext cost for candidate configs."""

from __future__ import annotations

import time

import tenseal as ts
import torch
from monai.networks.nets import UNet

from fedmed.metrics import dice_loss


def bench(channels, res_units, dropout, patch=64, batch=2):
    m = UNet(
        spatial_dims=3,
        in_channels=1,
        out_channels=3,
        channels=channels,
        strides=(2, 2, 2, 2),
        num_res_units=res_units,
        dropout=dropout,
        norm="INSTANCE",
        bias=True,
        up_kernel_size=3,
    )
    params = sum(p.numel() for p in m.parameters())
    x = torch.randn(batch, 1, patch, patch, patch)
    y = torch.randint(0, 3, (batch, patch, patch, patch))
    opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    t = time.time()
    for _ in range(2):
        opt.zero_grad()
        out = m(x)
        loss = dice_loss(out, y, 3)
        loss.backward()
        opt.step()
    step = (time.time() - t) / 2

    ctx = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=16384,
        coeff_mod_bit_sizes=[60, 40, 40, 60],
    )
    ctx.global_scale = float(2**30)
    vec = torch.randn(params).numpy()
    t = time.time()
    blob = ts.ckks_vector(ctx, vec).serialize()
    he_time = time.time() - t

    print(
        f"ch={str(channels):22} res={res_units} params={params:>10,} "
        f"step={step:6.3f}s ct={len(blob) / 1e6:8.1f}MB he_enc={he_time:5.2f}s"
    )
    return params


if __name__ == "__main__":
    print()
    bench((16, 32, 64, 128, 256), 2, 0.2)
    bench((8, 16, 32, 64, 128), 2, 0.2)
    bench((8, 16, 32, 64, 128), 1, 0.1)
    bench((8, 16, 32, 64), 1, 0.1)
    bench((16, 32, 64, 128), 1, 0.1)
    bench((8, 16, 32, 64, 128, 256), 1, 0.1)
    print()
