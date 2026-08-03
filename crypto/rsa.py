"""RSA helper functions used by the cryptographic engine."""

from __future__ import annotations

from base64 import b64decode

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key


class RSAService:
	"""Executes RSA signature verification operations."""

	@staticmethod
	def verify_sha256_pkcs1v15(payload: bytes, signature_b64: str, public_key_pem: str) -> None:
		"""Verify a PKCS#1 v1.5 SHA-256 signature or raise an exception."""
		signature = b64decode(signature_b64)
		key = load_pem_public_key(public_key_pem.encode("utf-8"))
		key.verify(signature, payload, padding.PKCS1v15(), hashes.SHA256())

