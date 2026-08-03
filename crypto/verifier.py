"""High-level signature verifier wrapper around RSA helpers."""

from __future__ import annotations

from crypto.rsa import RSAService


class SignatureVerifier:
	"""Facade for algorithm-specific signature verification flows."""

	def verify(self, payload: bytes, signature_b64: str, public_key_pem: str) -> None:
		"""Verify SHA-256 PKCS#1 v1.5 signatures."""
		RSAService.verify_sha256_pkcs1v15(payload, signature_b64, public_key_pem)

