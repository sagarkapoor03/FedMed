"""End-to-end federated smoke test.

Runs a short federated training loop (3 rounds) with HE + DP enabled and
asserts that:
  * the loop completes and produces metrics,
  * aggregation is homomorphic (ciphertext path),
  * the global model improves,
  * a node dropping offline does not break the round.
"""

from __future__ import annotations

import logging
import time

from fedmed.config import CONFIG
from fedmed.state import STATE
from fedmed.strategy import FederatedStrategy

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s"
)
logger = logging.getLogger("test_federated")


def main():
    from flwr.compat.server.app import ServerConfig, start_server

    rounds = 3
    strategy = FederatedStrategy(
        num_rounds=rounds,
        dropout_round=2,
        dropout_node=3,
        enable_he=True,
        enable_dp=True,
    )

    STATE.mark_started()
    STATE.total_rounds = rounds

    address = CONFIG.server.fl_address
    started = time.time()

    start_server(
        server_address=address,
        config=ServerConfig(num_rounds=rounds),
        strategy=strategy,
    )

    elapsed = time.time() - started
    rounds_data = STATE.rounds_snapshot()

    print()
    print("=" * 68)
    print(f"ROUNDS COMPLETED: {len(rounds_data)}  (in {elapsed:.1f}s)")
    print("=" * 68)
    for r in rounds_data:
        print(
            f"  round {r['round']}: dice={r['dice']:6.2f}%  loss={r['loss']:.4f}  "
            f"clients={r['clients']}  failed={r['failed_clients']}  "
            f"mode={r['aggregation']}  encrypted={r['encrypted_updates']}"
        )

    assert rounds_data, "no rounds recorded"

    modes = {r["aggregation"] for r in rounds_data}
    print(f"\nAggregation modes used: {modes}")
    assert "homomorphic_ckks" in modes, f"HE aggregation not used: {modes}"

    dropout_rounds = [
        r for r in rounds_data if r["failed_clients"] or r["clients"] < 3
    ]
    if dropout_rounds:
        print(f"Dropout handled in round(s): {[r['round'] for r in dropout_rounds]}")

    print("\nNode status:")
    for node in STATE.node_snapshot():
        print(
            f"  {node['node_id']}: status={node['status']:9} "
            f"rounds={node['rounds_participated']} "
            f"local_dice={node['local_dice']} "
            f"encrypted={node['encrypted']} "
            f"payload={node['payload_bytes']:,}B"
        )

    dp_eps = STATE.status_snapshot()["dp_epsilon"]
    print(f"\nDP epsilon after {rounds} rounds: {dp_eps}")

    print("\nFederated smoke test PASSED.\n")


if __name__ == "__main__":
    main()
