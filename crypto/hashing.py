"""Hashing utility helpers for document and payload fingerprinting."""

from __future__ import annotations

import hashlib


class HashingService:
	"""Provides canonical hashing helpers used across cryptographic workflows."""

	@staticmethod
	def sha256_bytes(payload: bytes) -> bytes:
		"""Return SHA-256 digest bytes for a payload."""
		digest = hashlib.sha256()
		digest.update(payload)
		return digest.digest()

	@staticmethod
	def sha256_hex(payload: bytes) -> str:
		"""Return SHA-256 digest hex string for a payload."""
		return HashingService.sha256_bytes(payload).hex()

