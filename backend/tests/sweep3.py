"""Calibrate the DP-SGD operating point with the corrected (averaged) gradient."""

from __future__ import annotations

import json
import time

from .sweep import run_config

CONFIGS = [
    ("sgd lr.10 sig0.5",  "tiny",  "per_sample", 0.5, 1.0, 8, 2, 0.10, "sgd",   10),
    ("sgd lr.10 sig1.0",  "tiny",  "per_sample", 1.0, 1.0, 8, 2, 0.10, "sgd",   10),
    ("sgd lr.10 sig2.0",  "tiny",  "per_sample", 2.0, 1.0, 8, 2, 0.10, "sgd",   10),
    ("sgd lr.05 sig1.0",  "tiny",  "per_sample", 1.0, 1.0, 8, 2, 0.05, "sgd",   10),
    ("sgd lr.05 sig0.5",  "tiny",  "per_sample", 0.5, 1.0, 8, 2, 0.05, "sgd",   10),
    ("sgd lr.20 sig1.0",  "tiny",  "per_sample", 1.0, 1.0, 8, 2, 0.20, "sgd",   10),
    ("sgd lr.20 sig0.5",  "tiny",  "per_sample", 0.5, 1.0, 8, 2, 0.20, "sgd",   10),
    ("sgd lr.10 sig1 c.3","tiny",  "per_sample", 1.0, 0.3, 8, 2, 0.10, "sgd",   10),
    ("sgd lr.10 noDP",    "tiny",  "none",       0.0, 1.0, 8, 2, 0.10, "sgd",   10),
]


def main() -> None:
    results = []
    print(f"{'config':<20}{'params':>10}{'eps':>11}{'dice':>9}{'best':>8}{'acc':>8}{'time':>8}")
    print("-" * 74)
    for (label, model, dp, sigma, clip, batch, epochs, lr, opt, rounds) in CONFIGS:
        t0 = time.time()
        r = run_config(model, dp, sigma, clip, batch, epochs, lr, opt, rounds)
        results.append({**r, "label": label})
        print(f"{label:<20}{r['params']:>10,}{r['epsilon']:>11.3f}"
              f"{r['final_dice']:>9.2f}{r['best_dice']:>8.2f}"
              f"{r['final_accuracy']:>8.2f}{time.time()-t0:>7.0f}s")
        with open("logs/sweep3_results.json", "w") as fh:
            json.dump(results, fh, indent=2)


if __name__ == "__main__":
    main()
