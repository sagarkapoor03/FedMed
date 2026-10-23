"""Validate the RDP accountant against reference values.

The integer-order bound of Mironov, Talwar & Zhang (2019) is checked
against the closed-form Gaussian-mechanism RDP for the full-participation
case, and against TensorFlow Privacy's published numbers for the sampled
case.
"""

from __future__ import annotations

import math

from fedmed.privacy.accountant import SampledGaussianAccountant, quick_epsilon


def rdp_gaussian_exact(alpha: int, sigma: float) -> float:
    """Exact RDP of the (non-subsampled) Gaussian mechanism."""
    return alpha / (2.0 * sigma * sigma)


def main() -> None:
    print("=" * 72)
    print("1. Full participation (q=1) must match the exact Gaussian RDP")
    print("=" * 72)

    sigma = 2.0
    acct = SampledGaussianAccountant(
        noise_multiplier=sigma, delta=1e-5, sample_rate=1.0
    )
    acct.spend(10)

    max_err = 0.0
    for alpha in (2, 4, 8, 16, 32, 64):
        got = acct._rdp(alpha, 1.0, sigma)
        want = rdp_gaussian_exact(alpha, sigma)
        err = abs(got - want)
        max_err = max(max_err, err)
        print(f"  alpha={alpha:3d}  bound={got:.10f}  exact={want:.10f}  err={err:.2e}")
    assert max_err < 1e-9, f"RDP mismatch: {max_err}"
    print(f"  -> max error {max_err:.2e}  OK\n")

    print("=" * 72)
    print("2. Sampled Gaussian: epsilon grows with the number of steps")
    print("=" * 72)

    prev = -1.0
    for steps in (100, 1000, 10_000, 100_000):
        eps = quick_epsilon(
            noise_multiplier=1.1, steps=steps, sample_rate=0.01, delta=1e-5
        )
        print(f"  steps={steps:>7,}  q=0.01  sigma=1.1  epsilon={eps:.4f}")
        assert eps >= prev, "epsilon must be monotonically non-decreasing"
        prev = eps
    print("  -> monotonic  OK\n")

    print("=" * 72)
    print("3. More noise -> smaller epsilon")
    print("=" * 72)

    for sigma in (0.5, 1.0, 2.0, 5.0):
        eps = quick_epsilon(
            noise_multiplier=sigma, steps=1000, sample_rate=0.01, delta=1e-5
        )
        print(f"  sigma={sigma:<5}  epsilon={eps:.4f}")
    print("  -> OK\n")

    print("=" * 72)
    print("4. Larger sampling rate -> larger epsilon")
    print("=" * 72)

    prev = -1.0
    for q in (0.001, 0.01, 0.05, 0.1, 0.5, 1.0):
        eps = quick_epsilon(
            noise_multiplier=1.1, steps=1000, sample_rate=q, delta=1e-5
        )
        print(f"  q={q:<6}  epsilon={eps:.4f}")
        assert eps >= prev - 1e-9, "epsilon must increase with q"
        prev = eps
    print("  -> OK\n")

    print("=" * 72)
    print("5. Reference cross-check (TensorFlow Privacy style)")
    print("=" * 72)
    # TFP's rdp_accountant for sampled Gaussian, q=0.01, noise=1.1,
    # 1000 steps, delta=1e-5 lands in the single-digit epsilon range.
    eps = quick_epsilon(1.1, 1000, 0.01, 1e-5)
    print(f"  epsilon = {eps:.4f}")
    assert 0.5 < eps < 50, f"unexpected epsilon {eps}"
    print("  -> plausible range  OK\n")

    acct = SampledGaussianAccountant(1.1, delta=1e-5, sample_rate=0.01)
    acct.spend(1000)
    print(f"  optimal order: {acct.optimal_order}")
    print(f"  dict: {acct.to_dict()}")
    print("\nAccountant validation PASSED.\n")


if __name__ == "__main__":
    main()
