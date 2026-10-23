"""Sweep the privacy/utility trade-off for the FedMed DP mechanism.

Runs the in-process federated simulator over a grid of (model size,
noise multiplier, optimiser) configurations and prints the resulting
accuracy together with the matching (epsilon, delta) privacy budget so an
operating point can be chosen from data rather than guesswork.
"""

from __future__ import annotations

import json
import time

import numpy as np
import torch

from fedmed.config import CONFIG
from fedmed.data import build_local_loaders, load_global_validation, make_loader
from fedmed.metrics import evaluate_model
from fedmed.privacy.accountant import quick_epsilon

from .sim_fl import build, local_train


def run_config(
    model_name: str,
    dp_mode: str,
    sigma: float,
    clip: float,
    batch: int,
    epochs: int,
    lr: float,
    opt_name: str,
    rounds: int,
    dropout_round: int = 0,
) -> dict:
    torch.manual_seed(0)
    np.random.seed(0)

    model = build(model_name)
    nparams = sum(p.numel() for p in model.parameters())
    global_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

    loaders, sizes = {}, {}
    for h in CONFIG.hospitals:
        tr, _ = build_local_loaders(h.hospital_id, batch_size=batch)
        loaders[h.hospital_id] = tr
        sizes[h.hospital_id] = len(tr.dataset)

    val_x, val_y = load_global_validation()
    val_loader = make_loader(val_x, val_y, batch_size=4, shuffle=False)

    history = []
    total_steps = 0
    for rnd in range(1, rounds + 1):
        active = list(loaders)
        if dropout_round and rnd == dropout_round:
            active = active[:-1]

        total = sum(sizes[h] for h in active)
        deltas, weights = {}, {}
        for h in active:
            d, _, _ = local_train(
                model, loaders[h], global_state, epochs, lr,
                dp_mode, sigma, clip, opt_name,
            )
            deltas[h] = d
            weights[h] = sizes[h] / total

        agg = None
        for h in active:
            w = weights[h]
            contrib = {k: v * w for k, v in deltas[h].items()}
            agg = contrib if agg is None else {k: agg[k] + contrib[k] for k in agg}

        global_state = {
            k: (global_state[k].to(torch.float64) + agg[k]).to(
                dtype=global_state[k].dtype
            )
            for k in global_state
        }
        model.load_state_dict(global_state)

        m = evaluate_model(model, val_loader, 3)
        history.append({"round": rnd, "dice": m["dice"], "loss": m["loss"],
                        "accuracy": m["accuracy"]})
        total_steps += epochs * max(
            1, sum(
                (sizes[h] + batch - 1) // batch for h in active
            )
        ) // max(len(active), 1)

    # Privacy budget: per-sample DP spends one mechanism invocation per
    # optimiser step; the sampling rate is batch / local cohort size.
    local_n = sum(sizes.values()) / len(sizes)
    q = min(batch / max(local_n, 1), 1.0)
    eps = 0.0
    if dp_mode == "per_sample" and sigma > 0:
        eps = quick_epsilon(sigma, total_steps, q, CONFIG.privacy.dp_delta)

    return {
        "model": model_name,
        "params": nparams,
        "dp": dp_mode,
        "sigma": sigma,
        "clip": clip,
        "batch": batch,
        "epochs": epochs,
        "lr": lr,
        "opt": opt_name,
        "rounds": rounds,
        "steps": total_steps,
        "q": round(q, 4),
        "epsilon": round(eps, 3),
        "final_dice": history[-1]["dice"],
        "best_dice": max(h["dice"] for h in history),
        "final_accuracy": history[-1]["accuracy"],
        "history": history,
    }


CONFIGS = [
    # (label, model, dp, sigma, clip, batch, epochs, lr, opt, rounds)
    ("tiny/noDP",      "tiny",  "none",       0.0,  1.0,  8, 2, 1e-3, "adamw", 10),
    ("small/noDP",     "small", "none",       0.0,  1.0,  8, 2, 1e-3, "adamw", 10),
    ("tiny/ps s1.1",   "tiny",  "per_sample", 1.1,  1.0,  8, 2, 1e-3, "adamw", 10),
    ("tiny/ps s0.3",   "tiny",  "per_sample", 0.3,  1.0,  8, 2, 1e-3, "adamw", 10),
    ("tiny/ps s0.1",   "tiny",  "per_sample", 0.1,  1.0,  8, 2, 1e-3, "adamw", 10),
    ("tiny/ps s1.1sgd","tiny",  "per_sample", 1.1,  1.0,  8, 2, 1e-2, "sgd",   10),
    ("tiny/upd s1e-3","tiny",  "update",     1e-3, 1.0,  8, 2, 1e-3, "adamw", 10),
    ("tiny/ps s0.3 c3","tiny",  "per_sample", 0.3,  3.0,  8, 2, 1e-3, "adamw", 10),
]


def main() -> None:
    results = []
    print(f"{'config':<18}{'params':>10}{'sigma':>8}{'steps':>7}{'q':>8}"
          f"{'eps':>12}{'dice':>9}{'best':>8}{'acc':>8}{'time':>8}")
    print("-" * 96)
    for (label, model, dp, sigma, clip, batch, epochs, lr, opt, rounds) in CONFIGS:
        t0 = time.time()
        r = run_config(model, dp, sigma, clip, batch, epochs, lr, opt, rounds)
        results.append({**r, "label": label})
        print(f"{label:<18}{r['params']:>10,}{sigma:>8}{r['steps']:>7}{r['q']:>8}"
              f"{r['epsilon']:>12.3f}{r['final_dice']:>9.2f}{r['best_dice']:>8.2f}"
              f"{r['final_accuracy']:>8.2f}{time.time()-t0:>7.0f}s")
        with open("logs/sweep_results.json", "w") as fh:
            json.dump(results, fh, indent=2)


if __name__ == "__main__":
    main()
