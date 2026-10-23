"""Benchmark CKKS ciphertext payload size across modulus-chain settings."""

from __future__ import annotations

import time

import numpy as np
import tenseal as ts
from monai.networks.nets import UNet


def build(ch, st, res_units=2):
    return UNet(
        spatial_dims=3, in_channels=1, out_channels=3, channels=ch, strides=st,
        num_res_units=res_units, dropout=0.2, norm="INSTANCE", bias=True,
        up_kernel_size=3,
    )


def bench(ch, st, poly, bits, res_units=2):
    m = build(ch, st, res_units)
    n = sum(p.numel() for p in m.parameters())
    vec = np.concatenate([
        v.detach().cpu().reshape(-1).numpy().astype(np.float64)
        for v in m.state_dict().values()
    ])

    ctx = ts.context(ts.SCHEME_TYPE.CKKS, poly_modulus_degree=poly,
                      coeff_mod_bit_sizes=list(bits))
    ctx.global_scale = float(2**30)

    t0 = time.time()
    ct = ts.ckks_vector(ctx, vec)
    t1 = time.time()
    blob = ct.serialize()
    t2 = time.time()
    out = np.array(ct.decrypt())
    t3 = time.time()
    err = float(np.max(np.abs(out - vec)))
    print(f"params={n:>9,} poly={poly:>5} bits={str(bits):>22} "
          f"enc={t1-t0:5.2f}s dec={t3-t2:5.2f}s size={len(blob)/1e6:6.2f}MB "
          f"err={err:.2e}")


if __name__ == "__main__":
    C = (8, 16, 32, 64)
    S = (2, 2, 2)
    for poly in (8192, 16384):
        for bits in [(60, 40, 40, 60), (40, 40, 40, 40), (30, 30, 30, 30), (60, 30, 30, 60)]:
            bench(C, S, poly, bits)
    print()
    C2 = (16, 32, 64, 128)
    for bits in [(60, 40, 40, 60), (40, 40, 40, 40), (30, 30, 30, 30)]:
        bench(C2, S, 16384, bits, res_units=1)
