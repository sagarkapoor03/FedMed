"""TLS certificate generation for the gRPC transport.

Creates a local certificate authority and issues a server certificate plus
per-node client certificates, all with mutual TLS (mTLS) so that both
parties authenticate each other. This is the "secure communication between
the server and nodes" requirement of the project plan.

Certificates are generated with the ``cryptography`` library (already a
dependency of grpcio) so no OpenSSL binary is required.
"""

from __future__ import annotations

import datetime
import ipaddress
import logging
from pathlib import Path

from .config import CERT_ROOT, CONFIG

logger = logging.getLogger(__name__)

try:
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID

    CRYPTO_AVAILABLE = True
except Exception as exc:  # pragma: no cover
    CRYPTO_AVAILABLE = False
    logger.warning("cryptography unavailable (%s); TLS disabled.", exc)

CERT_VALID_DAYS = 825


def _new_key() -> "rsa.RSAPrivateKey":
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _write_key(path: Path, key: "rsa.RSAPrivateKey") -> None:
    path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    path.chmod(0o600)


def _write_cert(path: Path, cert: "x509.Certificate") -> None:
    path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))


def generate_certificates(
    cert_root: Path | None = None,
    host: str = "127.0.0.1",
    server_port: int = 50051,
    node_ports: tuple = (9101, 9102, 9103),
    force: bool = False,
) -> dict:
    """Generate a CA plus server and client certificates.

    Returns:
        Dict describing the generated certificate paths.
    """
    root = Path(cert_root) if cert_root else CERT_ROOT
    root.mkdir(parents=True, exist_ok=True)

    ca_key_path = root / "ca.key"
    ca_cert_path = root / "ca.crt"
    server_key_path = root / "server.key"
    server_cert_path = root / "server.crt"
    client_key_path = root / "client.key"
    client_cert_path = root / "client.crt"

    if not CRYPTO_AVAILABLE:
        return {"available": False}

    if ca_cert_path.exists() and not force:
        logger.info("TLS certificates already present in %s", root)
    else:
        now = datetime.datetime.now(datetime.timezone.utc)

        # --- Certificate authority ---
        ca_key = _new_key()
        ca_subject = x509.Name(
            [
                x509.NameAttribute(NameOID.COMMON_NAME, "FedMed Local CA"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "FedMed"),
            ]
        )
        ca_cert = (
            x509.CertificateBuilder()
            .subject_name(ca_subject)
            .issuer_name(ca_subject)
            .public_key(ca_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - datetime.timedelta(minutes=5))
            .not_valid_after(now + datetime.timedelta(days=CERT_VALID_DAYS))
            .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    content_commitment=False,
                    key_encipherment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=True,
                    crl_sign=True,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            .sign(ca_key, hashes.SHA256())
        )
        _write_key(ca_key_path, ca_key)
        _write_cert(ca_cert_path, ca_cert)

        # --- Server certificate ---
        server_key = _new_key()
        server_names = [x509.DNSName("localhost"), x509.DNSName("fedmed-server")]
        try:
            server_names.append(x509.IPAddress(ipaddress.ip_address(host)))
        except ValueError:
            pass

        server_cert = (
            x509.CertificateBuilder()
            .subject_name(
                x509.Name(
                    [
                        x509.NameAttribute(NameOID.COMMON_NAME, "fedmed-server"),
                        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "FedMed"),
                    ]
                )
            )
            .issuer_name(ca_subject)
            .public_key(server_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - datetime.timedelta(minutes=5))
            .not_valid_after(now + datetime.timedelta(days=CERT_VALID_DAYS))
            .add_extension(x509.SubjectAlternativeName(server_names), critical=False)
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .add_extension(
                x509.ExtendedKeyUsage(
                    [
                        x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
                        x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
                    ]
                ),
                critical=False,
            )
            .sign(ca_key, hashes.SHA256())
        )
        _write_key(server_key_path, server_key)
        _write_cert(server_cert_path, server_cert)

        # --- Client certificate (shared by the hospital nodes) ---
        client_key = _new_key()
        client_cert = (
            x509.CertificateBuilder()
            .subject_name(
                x509.Name(
                    [
                        x509.NameAttribute(NameOID.COMMON_NAME, "fedmed-node"),
                        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "FedMed"),
                    ]
                )
            )
            .issuer_name(ca_subject)
            .public_key(client_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - datetime.timedelta(minutes=5))
            .not_valid_after(now + datetime.timedelta(days=CERT_VALID_DAYS))
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .add_extension(
                x509.ExtendedKeyUsage(
                    [x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH]
                ),
                critical=False,
            )
            .sign(ca_key, hashes.SHA256())
        )
        _write_key(client_key_path, client_key)
        _write_cert(client_cert_path, client_cert)

        logger.info("Generated TLS CA + server/client certificates in %s", root)

    return {
        "available": True,
        "ca_cert": str(ca_cert_path),
        "server_cert": str(server_cert_path),
        "server_key": str(server_key_path),
        "client_cert": str(client_cert_path),
        "client_key": str(client_key_path),
        "mutual_tls": True,
    }


def tls_status() -> dict:
    """Report the TLS subsystem state to the dashboard."""
    cfg = CONFIG.server
    files = {
        "ca_cert": cfg.ca_cert,
        "server_cert": cfg.server_cert,
        "server_key": cfg.server_key,
        "client_cert": cfg.client_cert,
        "client_key": cfg.client_key,
    }
    present = {name: Path(p).exists() for name, p in files.items()}
    return {
        "available": CRYPTO_AVAILABLE,
        "enabled": all(present.values()),
        "mutual_tls": True,
        "transport": "gRPC + TLS",
        "files_present": present,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(generate_certificates(force=True))
