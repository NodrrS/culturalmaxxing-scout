"""
#############################################################################
### Deterministic asymmetric key generator (passphrase + KDF)
###
### @file keys_generator_dtrmnstc.py
### @Sebastian Russo
### @date: 2026
#############################################################################

Derives a reproducible Ed25519 key pair from a passphrase using PBKDF2-HMAC-SHA256.

Unlike keys_generator.py (random RSA via OS CSPRNG), the same passphrase + salt +
KDF parameters always produce the same key pair. Salt and KDF settings are written
to a small metadata JSON file so keys can be reproduced later.

NOTE: Ed25519 keys are not compatible with en_de_crypt.py in this template, which
expects RSA keys for OAEP encryption.
"""

from __future__ import annotations

import argparse
import base64
import getpass
import json
import secrets
from pathlib import Path
from typing import Optional

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from src.utils.custom_logger import log_handler

DEFAULT_ITERATIONS = 200_000
DEFAULT_METADATA_NAME = "key_derivation.json"
DEFAULT_PRIVATE_NAME = "private_key.pem"
DEFAULT_PUBLIC_NAME = "public_key.pem"


def derive_ed25519_keypair(
    passphrase: bytes,
    salt: bytes,
    iterations: int = DEFAULT_ITERATIONS,
):
    if not passphrase:
        raise ValueError("Passphrase must not be empty.")
    if not salt:
        raise ValueError("Salt must not be empty.")
    if iterations < 1:
        raise ValueError("PBKDF2 iterations must be at least 1.")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=default_backend(),
    )
    seed = kdf.derive(passphrase)
    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(seed)
    return private_key, private_key.public_key()


def export_key_pems(
    private_key: ed25519.Ed25519PrivateKey,
    public_key: ed25519.Ed25519PublicKey,
    pem_password: Optional[bytes] = None,
):
    if pem_password:
        encryption = serialization.BestAvailableEncryption(pem_password)
    else:
        encryption = serialization.NoEncryption()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption,
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_pem, public_pem


def write_metadata(
    metadata_path: Path,
    *,
    algorithm: str,
    salt: bytes,
    iterations: int,
    private_key_file: str,
    public_key_file: str,
) -> None:
    metadata = {
        "algorithm": algorithm,
        "kdf": "PBKDF2-HMAC-SHA256",
        "iterations": iterations,
        "salt_b64": base64.b64encode(salt).decode("ascii"),
        "private_key_file": private_key_file,
        "public_key_file": public_key_file,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


def generate_deterministic_keys(
    passphrase: bytes,
    output_dir: Path,
    *,
    salt: Optional[bytes] = None,
    iterations: int = DEFAULT_ITERATIONS,
    pem_password: Optional[bytes] = None,
    private_name: str = DEFAULT_PRIVATE_NAME,
    public_name: str = DEFAULT_PUBLIC_NAME,
    metadata_name: str = DEFAULT_METADATA_NAME,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)

    used_salt = salt if salt is not None else secrets.token_bytes(16)
    private_key, public_key = derive_ed25519_keypair(
        passphrase=passphrase,
        salt=used_salt,
        iterations=iterations,
    )
    private_pem, public_pem = export_key_pems(private_key, public_key, pem_password)

    private_path = output_dir / private_name
    public_path = output_dir / public_name
    metadata_path = output_dir / metadata_name

    private_path.write_bytes(private_pem)
    public_path.write_bytes(public_pem)
    write_metadata(
        metadata_path,
        algorithm="Ed25519",
        salt=used_salt,
        iterations=iterations,
        private_key_file=private_name,
        public_key_file=public_name,
    )

    return {
        "private_path": private_path,
        "public_path": public_path,
        "metadata_path": metadata_path,
        "salt": used_salt,
        "iterations": iterations,
    }


def _parse_salt(value: str) -> bytes:
    if value.startswith("b64:"):
        return base64.b64decode(value[4:], validate=True)
    return value.encode("utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a deterministic Ed25519 key pair from a passphrase using PBKDF2."
        )
    )
    parser.add_argument("-p", "--passphrase", help="Passphrase for key derivation.")
    parser.add_argument(
        "-s",
        "--salt",
        help="Salt for PBKDF2 (plain text or b64:...). Random if omitted.",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=DEFAULT_ITERATIONS,
        help=f"PBKDF2 iteration count (default: {DEFAULT_ITERATIONS}).",
    )
    parser.add_argument("-o", "--output-dir", default=".", help="Output directory.")
    parser.add_argument("--private-name", default=DEFAULT_PRIVATE_NAME)
    parser.add_argument("--public-name", default=DEFAULT_PUBLIC_NAME)
    parser.add_argument("--metadata-name", default=DEFAULT_METADATA_NAME)
    parser.add_argument(
        "--pem-password",
        nargs="?",
        const="",
        help="Optional password to encrypt the private PEM.",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    passphrase_text = args.passphrase
    if not passphrase_text:
        passphrase_text = getpass.getpass("Passphrase: ")
        confirm = getpass.getpass("Confirm passphrase: ")
        if passphrase_text != confirm:
            log_handler.error("Passphrases do not match.")
            return 1

    salt = _parse_salt(args.salt) if args.salt else None

    pem_password: Optional[bytes] = None
    if args.pem_password is not None:
        pem_password_text = args.pem_password or getpass.getpass("Private PEM password: ")
        pem_password = pem_password_text.encode("utf-8")

    try:
        result = generate_deterministic_keys(
            passphrase=passphrase_text.encode("utf-8"),
            output_dir=Path(args.output_dir),
            salt=salt,
            iterations=args.iterations,
            pem_password=pem_password,
            private_name=args.private_name,
            public_name=args.public_name,
            metadata_name=args.metadata_name,
        )
    except ValueError as exc:
        log_handler.error(str(exc))
        return 1

    log_handler.info("Deterministic Ed25519 keys generated successfully!")
    log_handler.info(f"Private key: {result['private_path']}")
    log_handler.info(f"Public key:  {result['public_path']}")
    log_handler.info(f"Metadata:    {result['metadata_path']}")
    if args.salt is None:
        log_handler.info(
            "A random salt was generated and saved in the metadata file."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
