"""Benchmark CKKS ciphertext size / time for candidate model sizes."""

from __future__ import annotations

import time

import numpy as np
import tenseal as ts
from monai.networks.nets import UNet


def build(ch, st, res_units=1):
    return UNet(
        spatial_dims=3, in_channels=1, out_channels=3, channels=ch, strides=st,
        num_res_units=res_units, dropout=0.2, norm="INSTANCE", bias=True,
        up_kernel_size=3,
    )


def bench(ch, st, poly, bits, res_units=1):
    m = build(ch, st, res_units)
    n = sum(p.numel() for p in m.parameters())
    vec = np.concatenate([v.detach().cpu().reshape(-1).numpy().astype(np.float64)
                          for v in m.state_dict().values()])

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
    print(f"params={n:>9,} poly={poly} bits={bits} "
          f"enc={t1-t0:5.2f}s ser={t2-t1:5.2f}s dec={t3-t2:5.2f}s "
          f"size={len(blob)/1e6:7.2f}MB  err={err:.2e}  "
          f"expansion={len(blob)/ (n*4):.1f}x")
    return len(blob)


if __name__ == "__main__":
    bench((16, 32, 64, 128), (2, 2, 2), 16384, (60, 40, 40, 60))
    bench((8, 16, 32, 64, 128), (2, 2, 2, 2), 16384, (60, 40, 40, 60))
    bench((16, 32, 64, 128), (2, 2, 2), 8192, (60, 40, 40, 60))
    bench((16, 32, 64, 128), (2, 2, 2), 8192, (40, 40, 40, 40))
    bench((8, 16, 32, 64, 128), (2, 2, 2, 2), 8192, (40, 40, 40, 40))
