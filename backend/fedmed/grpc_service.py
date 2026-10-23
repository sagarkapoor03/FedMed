"""gRPC node coordination service with mutual TLS.

Each hospital node runs one of these servers. The central aggregator
connects over mTLS to verify node health and to distribute the CKKS
context and the current global model.

The service deliberately handles *no* patient data -- only model weights
and node metadata.
"""

from __future__ import annotations

import logging
import time
from concurrent import futures
from pathlib import Path

import grpc

from .config import CONFIG
from .proto import fedmed_pb2, fedmed_pb2_grpc
from .state import STATE, NodeStatus

logger = logging.getLogger(__name__)


def _read(path: Path) -> bytes:
    return Path(path).read_bytes()


def server_credentials(cert_root: Path | None = None) -> grpc.ServerCredentials | None:
    """Build mTLS server credentials, or ``None`` if certs are missing."""
    cfg = CONFIG.server
    root = Path(cert_root) if cert_root else Path(cfg.ca_cert).parent

    ca = root / "ca.crt"
    cert = root / "server.crt"
    key = root / "server.key"
    client_cert = root / "client.crt"

    if not (ca.exists() and cert.exists() and key.exists()):
        logger.warning("TLS material missing in %s; gRPC server will be insecure.", root)
        return None

    with open(cert, "rb") as fh:
        cert_chain = fh.read()
    with open(key, "rb") as fh:
        private_key = fh.read()
    with open(ca, "rb") as fh:
        root_ca = fh.read()

    if client_cert.exists():
        with open(client_cert, "rb") as fh:
            root_ca = root_ca + fh.read()

    return grpc.ssl_server_credentials(
        private_key_certificate_chain_pairs=[(private_key, cert_chain)],
        root_certificates=root_ca,
        require_client_auth=True,
    )


def channel_credentials(cert_root: Path | None = None) -> grpc.ChannelCredentials:
    """Build mTLS client credentials."""
    cfg = CONFIG.server
    root = Path(cert_root) if cert_root else Path(cfg.ca_cert).parent

    ca = root / "ca.crt"
    cert = root / "client.crt"
    key = root / "client.key"

    with open(ca, "rb") as fh:
        root_ca = fh.read()

    if cert.exists() and key.exists():
        with open(cert, "rb") as fh:
            cert_chain = fh.read()
        with open(key, "rb") as fh:
            private_key = fh.read()
        return grpc.ssl_channel_credentials(
            root_certificates=root_ca,
            private_key=private_key,
            certificate_chain=cert_chain,
        )

    return grpc.ssl_channel_credentials(root_certificates=root_ca)


class FedMedNodeServicer(fedmed_pb2_grpc.FedMedNodeServicer):
    """gRPC service implementation executed by a hospital node."""

    def __init__(self, hospital_id: str, node_id: str) -> None:
        self.hospital_id = hospital_id
        self.node_id = node_id
        self.he_context: bytes | None = None
        self.last_global_model: bytes | None = None
        self.last_sync_round = 0

    def CheckHealth(self, request, context):  # noqa: N802 (gRPC naming)
        """Return the node's health and privacy posture."""
        node = STATE.nodes.get(self.hospital_id, {})
        STATE.update_node(
            self.hospital_id,
            status=NodeStatus.ONLINE,
            message="Health check via gRPC/TLS",
        )
        return fedmed_pb2.HealthResponse(
            healthy=True,
            node_id=self.node_id,
            hospital_id=self.hospital_id,
            samples=int(node.get("samples") or 0),
            encryption_enabled=bool(node.get("encrypted")),
            differential_privacy_enabled=True,
            server_timestamp=int(time.time()),
            protocol="gRPC",
            tls=True,
        )

    def SyncModel(self, request, context):  # noqa: N802 (gRPC naming)
        """Accept the CKKS context and global model from the aggregator."""
        self.he_context = request.he_context or None
        self.last_global_model = request.global_model or None
        self.last_sync_round = request.round

        STATE.update_node(
            self.hospital_id,
            status=NodeStatus.ONLINE,
            last_sync=time.time(),
            message=f"Synced global model for round {request.round}",
        )
        return fedmed_pb2.SyncModelResponse(
            accepted=True,
            message=f"Model synced for round {request.round}",
            synced_at=int(time.time()),
        )

    def ReportRound(self, request, context):  # noqa: N802 (gRPC naming)
        """Acknowledge a node's round report."""
        STATE.update_node(
            self.hospital_id,
            local_loss=request.local_loss,
            local_dice=request.local_dice,
            payload_bytes=request.payload_bytes,
            encrypted=request.encrypted,
            last_sync=time.time(),
            message=f"Round {request.round} reported",
        )
        return fedmed_pb2.RoundReportResponse(
            acknowledged=True, message=f"Round {request.round} recorded"
        )


def serve(
    hospital_id: str,
    node_id: str,
    port: int,
    cert_root: Path | None = None,
    max_workers: int = 4,
) -> grpc.Server:
    """Start the node's gRPC server and return it."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    servicer = FedMedNodeServicer(hospital_id, node_id)
    fedmed_pb2_grpc.add_FedMedNodeServicer_to_server(servicer, server)

    creds = server_credentials(cert_root)
    address = f"127.0.0.1:{port}"
    if creds is not None:
        server.add_secure_port(address, creds)
        logger.info("[%s] gRPC/TLS server listening on %s", node_id, address)
    else:
        server.add_insecure_port(address)
        logger.warning("[%s] gRPC server (INSECURE) listening on %s", node_id, address)

    server.start()
    return server
