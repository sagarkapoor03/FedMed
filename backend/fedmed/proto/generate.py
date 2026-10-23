"""Generate the gRPC Python stubs from ``fedmed.proto``.

Run:
    python -m fedmed.proto.generate
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

PROTO_DIR = Path(__file__).resolve().parent
PROTO_FILE = PROTO_DIR / "fedmed.proto"
OUT_DIR = PROTO_DIR


def _fix_relative_import(path: Path) -> None:
    """Rewrite the generated stub's absolute import into a relative one.

    ``grpc_tools.protoc`` emits ``import fedmed_pb2 as fedmed__pb2`` which
    only resolves when the output directory happens to be on ``sys.path``.
    Inside a package the import must be relative, otherwise the stub
    cannot be imported as ``fedmed.proto.fedmed_pb2_grpc``.
    """
    text = path.read_text()
    patched = re.sub(
        r"^import fedmed_pb2 as fedmed__pb2$",
        "from . import fedmed_pb2 as fedmed__pb2",
        text,
        flags=re.MULTILINE,
    )
    if patched != text:
        path.write_text(patched)


def generate() -> int:
    """Invoke grpcio-tools to produce ``fedmed_pb2.py`` and ``fedmed_pb2_grpc.py``."""
    cmd = [
        sys.executable,
        "-m",
        "grpc_tools.protoc",
        f"--proto_path={PROTO_DIR}",
        f"--python_out={OUT_DIR}",
        f"--grpc_python_out={OUT_DIR}",
        str(PROTO_FILE),
    ]
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd, check=False)
    if result.returncode == 0:
        _fix_relative_import(OUT_DIR / "fedmed_pb2_grpc.py")
        print("Generated:", OUT_DIR / "fedmed_pb2.py")
        print("Generated:", OUT_DIR / "fedmed_pb2_grpc.py")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(generate())
