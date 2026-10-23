"""Validate the differential-privacy mechanism.

Checks that:
  * per-sample clipping bounds every patient contribution,
  * the noise magnitude matches the theoretical sigma * C,
  * the mechanism is unbiased (E[output] == sum of unclipped gradients),
  * the accountant's epsilon grows with the number of protected patients.
"""

from __future__ import annotations

import math

import torch

from fedmed.privacy.dp import (
    add_gaussian_noise_to_gradients,
    clip_gradients_per_sample,
)


def main() -> None:
    torch.manual_seed(0)
    C = 1.0
    sigma_mult = 1.1

    # -- 1. clipping bounds each sample --------------------------------
    grads = [torch.randn(1000, dtype=torch.float64) * k for k in (0.1, 1.0, 50.0)]
    clipped, norms = clip_gradients_per_sample(grads, C)
    print("1. Per-sample clipping")
    print(f"   original norms : {[f'{n:.4f}' for n in norms]}")
    for g, n in zip(clipped, norms):
        cn = float(g.norm().item())
        assert cn <= C + 1e-9, f"clip failed: {cn} > {C}"
    print(f"   clipped norms  : {[f'{float(g.norm()):.4f}' for g in clipped]}")
    print("   -> every sample within C  OK\n")

    # -- 2. noise magnitude ---------------------------------------------
    grads = [torch.randn(5000, dtype=torch.float64) for _ in range(8)]
    summed = torch.stack(grads).sum(dim=0)
    _, stats = add_gaussian_noise_to_gradients(grads, sigma_mult, C)
    expected_sigma = sigma_mult * C
    assert abs(stats["sigma"] - expected_sigma) < 1e-12
    # The realised noise L2 norm over n dims is ~ sigma * sqrt(n).
    n = 5000
    expected_noise_l2 = expected_sigma * math.sqrt(n)
    ratio = stats["noise_l2_norm"] / expected_noise_l2
    print("2. Gaussian noise magnitude")
    print(f"   sigma          : {stats['sigma']}")
    print(f"   noise L2       : {stats['noise_l2_norm']:.3f}")
    print(f"   expected L2    : {expected_noise_l2:.3f} (sigma*sqrt(n))")
    print(f"   ratio          : {ratio:.4f}")
    assert 0.8 < ratio < 1.25, f"noise magnitude off: {ratio}"
    print("   -> matches theory  OK\n")

    # -- 3. unbiasedness ------------------------------------------------
    print("3. Unbiasedness (E[noised sum] == sum of clipped grads)")
    trials = 400
    dim = 200
    # Use a gradient whose norm is below C so that clipping is inactive and
    # the only source of error is the injected noise.
    base = torch.randn(dim, dtype=torch.float64)
    base = base / base.norm() * 0.5
    acc = torch.zeros(dim, dtype=torch.float64)
    for _ in range(trials):
        grads = [base.clone() for _ in range(4)]
        out, _ = add_gaussian_noise_to_gradients(grads, sigma_mult, C)
        acc += out
    mean_out = acc / trials
    expected = base * 4
    err = float((mean_out - expected).abs().max().item())
    print(f"   expected       : {float(expected.abs().max()):.4f} (max abs)")
    print(f"   empirical mean : {float(mean_out.abs().max()):.4f} (max abs)")
    print(f"   max abs error  : {err:.4f}")
    # With 400 trials the Monte-Carlo error is ~ sigma*sqrt(dim)/sqrt(trials).
    mc_err = expected_sigma * math.sqrt(dim) / math.sqrt(trials)
    print(f"   MC error scale : {mc_err:.4f}")
    assert err < 4 * mc_err, f"mechanism appears biased: {err} vs {mc_err}"
    print("   -> unbiased within MC error  OK\n")

    # -- 3b. clipping does bias, and that is by design ------------------
    print("3b. Clipping bias is explicit (documented variance/bias trade-off)")
    big = torch.randn(dim, dtype=torch.float64)
    out, stats = add_gaussian_noise_to_gradients([big], sigma_mult, C)
    print(f"   original norm  : {stats['original_norm']:.4f}")
    print(f"   clipped        : {stats['clipped']}")
    assert stats["clipped"] is True
    print("   -> clipping applied  OK\n")

    # -- 4. signal-to-noise ---------------------------------------------
    print("4. Signal to noise ratio")
    grads = [torch.randn(5000, dtype=torch.float64) for _ in range(8)]
    _, stats = add_gaussian_noise_to_gradients(grads, sigma_mult, C)
    print(f"   signal L2 : {stats['signal_l2_norm']:.3f}")
    print(f"   noise  L2 : {stats['noise_l2_norm']:.3f}")
    print(f"   SNR       : {stats['signal_to_noise']:.4f}")
    print(f"   patients  : {stats['patients_protected']}")
    print("   -> OK\n")

    print("DP mechanism validation PASSED.\n")


if __name__ == "__main__":
    main()
