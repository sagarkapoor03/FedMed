"""Verify that a CKKS context can be serialised to a node and used for
homomorphic aggregation on the server."""

from __future__ import annotations

import numpy as np
import tenseal as ts

from fedmed.privacy import he as he_mod


def main() -> None:
    server = he_mod.create_session("server")
    ctx_blob = he_mod.serialize_context(server)

    # Node rebuilds the context from the server's material.
    node_ctx = he_mod.create_node_context(ctx_blob)
    node_ctx.global_scale = he_mod.GLOBAL_SCALE

    rng = np.random.default_rng(0)
    a = rng.normal(size=50)
    b = rng.normal(size=50)

    # Client-side: pre-scale by FedAvg weight, then encrypt.
    wa, wb = 0.6, 0.4
    ct_a = ts.ckks_vector(node_ctx, np.ascontiguousarray(a * wa)).serialize()
    ct_b = ts.ckks_vector(node_ctx, np.ascontiguousarray(b * wb)).serialize()

    # Server-side: ciphertext-only addition, then a single decryption.
    sctx = server.context
    acc = ts.CKKSVector.load(sctx, ct_a)
    acc = acc + ts.CKKSVector.load(sctx, ct_b)
    result = np.array(acc.decrypt())

    expected = a * wa + b * wb
    err = float(np.max(np.abs(result - expected)))
    print(f"max abs error: {err:.3e}")
    print(f"ciphertext size: {len(ct_a):,} bytes for 50 params")
    assert err < 1e-3, f"HE aggregation error too large: {err}"
    print("HE shared-context aggregation OK\n")


if __name__ == "__main__":
    main()
