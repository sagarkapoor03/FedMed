"""Rényi Differential Privacy (RDP) accountant for the sampled Gaussian mechanism.

The FedMed nodes use *DP-SGD* (per-sample gradient clipping + Gaussian
noise) on top of a **subsampled** patient population: every local step uses
a minibatch drawn from the node's private patient cohort. Subsampling is
what makes a meaningful privacy budget possible at this scale -- a single
Gaussian perturbation over a ~600k-dimensional update vector would have to
be vanishingly small to keep the model trainable, whereas the
subsampled-Gaussian mechanism buys a ``sqrt(batch)`` amplification of the
signal-to-noise ratio *and* a ``q`` amplification of the privacy bound.

The accountant below implements the integer-order RDP bound of Mironov,
Talwar & Zhang (2019), "Rényi Differential Privacy of the Sampled Gaussian
Mechanism", which is the standard reference implementation used by Opacus
and TensorFlow Privacy.

Everything is computed in log space with ``logsumexp`` so that long
federated runs (hundreds of optimiser steps) do not overflow.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Sequence

logger = logging.getLogger(__name__)

#: Orders used by the accountant. Higher orders tighten the bound for
#: small sampling rates but lose numerical stability for large ones.
DEFAULT_ORDERS: tuple[int, ...] = tuple(range(2, 65)) + (128, 256, 512)


def _log_comb(n: int, k: int) -> float:
    """log(C(n, k)) computed stably."""
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def _logsumexp(values: Sequence[float]) -> float:
    """Numerically stable log(sum(exp(v)))."""
    if not values:
        return float("-inf")
    m = max(values)
    if m == float("-inf"):
        return m
    return m + math.log(sum(math.exp(v - m) for v in values))


@dataclass
class SampledGaussianAccountant:
    """RDP accountant for the sampled Gaussian mechanism.

    Attributes:
        noise_multiplier: Ratio of the injected noise std to the clipping
            threshold (``sigma = noise_multiplier * clip_norm``).
        delta: Target delta of the ``(epsilon, delta)`` guarantee.
        orders: Integer RDP orders to evaluate.
        steps: Number of optimiser steps charged so far.
        sample_rate: Probability of including a given patient in a step.
    """

    noise_multiplier: float
    delta: float = 1e-5
    orders: Sequence[int] = field(default_factory=lambda: DEFAULT_ORDERS)
    steps: int = 0
    sample_rate: float = 1.0

    # -- accounting ---------------------------------------------------
    def spend(self, steps: int = 1, sample_rate: float | None = None) -> None:
        """Charge ``steps`` mechanism invocations to the budget."""
        self.steps += steps
        if sample_rate is not None:
            self.sample_rate = sample_rate

    # -- RDP ----------------------------------------------------------
    def _log_a_alpha(self, alpha: int, q: float, sigma: float) -> float:
        """log(A_alpha) for the sampled Gaussian mechanism.

        ``A_alpha = sum_i C(alpha, i) (1-q)^(alpha-i) q^i exp(i(i-1)/(2 sigma^2))``

        The ``exp`` term is the moment of the Gaussian mechanism, computed
        in log space to avoid overflow for large ``alpha``.
        """
        log_q = math.log(q) if q > 0 else float("-inf")
        log_1mq = math.log1p(-q) if q < 1 else float("-inf")
        two_sigma_sq = 2.0 * sigma * sigma

        terms = []
        for i in range(alpha + 1):
            term = _log_comb(alpha, i)
            if alpha - i > 0:
                term += (alpha - i) * log_1mq
            if i > 0:
                term += i * log_q
            if two_sigma_sq > 0:
                term += (i * (i - 1)) / two_sigma_sq
            terms.append(term)
        return _logsumexp(terms)

    def _rdp(self, alpha: int, q: float, sigma: float) -> float:
        """RDP of order ``alpha`` for a single sampled Gaussian step."""
        if alpha == 1:
            # Order 1 is not covered by the theorem; skip it.
            return float("inf")
        log_a = self._log_a_alpha(alpha, q, sigma)
        return log_a / (alpha - 1)

    def _epsilon_for_order(self, alpha: int) -> float:
        """Convert the accumulated RDP into an epsilon for a given order."""
        if self.steps == 0:
            return 0.0

        q = min(max(self.sample_rate, 1e-12), 1.0)
        sigma = self.noise_multiplier
        if sigma <= 0:
            return float("inf")

        total_rdp = self.steps * self._rdp(alpha, q, sigma)
        # Improvement of the conversion bound over the naive one.
        improvement = math.log((alpha - 1) / alpha)
        eps = total_rdp - improvement
        eps += math.log(1.0 / self.delta) / (alpha - 1)
        return max(eps, 0.0)

    # -- public API ---------------------------------------------------
    @property
    def epsilon(self) -> float:
        """Best (smallest) epsilon across the evaluated RDP orders."""
        if self.steps == 0:
            return 0.0
        candidates = []
        for alpha in self.orders:
            if alpha <= 1:
                continue
            try:
                candidates.append(self._epsilon_for_order(alpha))
            except (ValueError, OverflowError):  # pragma: no cover - defensive
                continue
        if not candidates:
            return float("inf")
        return round(min(candidates), 6)

    @property
    def optimal_order(self) -> int:
        """The RDP order that produced the best epsilon."""
        best_alpha, best_eps = 0, float("inf")
        for alpha in self.orders:
            if alpha <= 1:
                continue
            try:
                eps = self._epsilon_for_order(alpha)
            except (ValueError, OverflowError):  # pragma: no cover
                continue
            if eps < best_eps:
                best_eps, best_alpha = eps, alpha
        return best_alpha

    def to_dict(self) -> dict:
        return {
            "epsilon": self.epsilon,
            "delta": self.delta,
            "noise_multiplier": self.noise_multiplier,
            "steps": self.steps,
            "sample_rate": round(self.sample_rate, 6),
            "optimal_order": self.optimal_order,
            "mechanism": "Sampled Gaussian (RDP accountant)",
        }


def quick_epsilon(
    noise_multiplier: float,
    steps: int,
    sample_rate: float,
    delta: float = 1e-5,
) -> float:
    """One-shot convenience wrapper around :class:`SampledGaussianAccountant`."""
    acct = SampledGaussianAccountant(
        noise_multiplier=noise_multiplier, delta=delta, sample_rate=sample_rate
    )
    acct.spend(steps)
    return acct.epsilon
