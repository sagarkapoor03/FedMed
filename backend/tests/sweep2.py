"""Focused sweep of the DP-SGD operating point (SGD optimiser family)."""

from __future__ import annotations

import json
import time

from .sweep import run_config

CONFIGS = [
    ("tiny sgd lr.01 sig1.1", "tiny",  "per_sample", 1.1, 1.0, 8, 2, 0.01, "sgd", 10),
    ("tiny sgd lr.01 sig2.0", "tiny",  "per_sample", 2.0, 1.0, 8, 2, 0.01, "sgd", 10),
    ("tiny sgd lr.01 sig5.0", "tiny",  "per_sample", 5.0, 1.0, 8, 2, 0.01, "sgd", 10),
    ("tiny sgd lr.03 sig1.1", "tiny",  "per_sample", 1.1, 1.0, 8, 2, 0.03, "sgd", 10),
    ("tiny sgd lr.03 sig2.0", "tiny",  "per_sample", 2.0, 1.0, 8, 2, 0.03, "sgd", 10),
    ("tiny sgd lr.10 sig2.0", "tiny",  "per_sample", 2.0, 1.0, 8, 2, 0.10, "sgd", 10),
    ("small sgd lr.03 sig2", "small", "per_sample", 2.0, 1.0, 8, 2, 0.03, "sgd", 10),
    ("tiny sgd noDP lr.03",  "tiny",  "none",       0.0, 1.0, 8, 2, 0.03, "sgd", 10),
    ("tiny sgd noDP lr.10",  "tiny",  "none",       0.0, 1.0, 8, 2, 0.10, "sgd", 10),
]


def main() -> None:
    results = []
    print(f"{'config':<24}{'params':>10}{'eps':>12}{'dice':>9}{'best':>8}{'acc':>8}{'time':>8}")
    print("-" * 80)
    for (label, model, dp, sigma, clip, batch, epochs, lr, opt, rounds) in CONFIGS:
        t0 = time.time()
        r = run_config(model, dp, sigma, clip, batch, epochs, lr, opt, rounds)
        results.append({**r, "label": label})
        print(f"{label:<24}{r['params']:>10,}{r['epsilon']:>12.3f}"
              f"{r['final_dice']:>9.2f}{r['best_dice']:>8.2f}"
              f"{r['final_accuracy']:>8.2f}{time.time()-t0:>7.0f}s")
        with open("logs/sweep2_results.json", "w") as fh:
            json.dump(results, fh, indent=2)


if __name__ == "__main__":
    main()
