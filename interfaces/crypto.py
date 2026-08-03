"""Crypto service interface contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from domain.value_objects.validation_result import CryptoVerificationResult


class ICryptoEngine(ABC):
	"""Contract for cryptographic signature verification."""

	@abstractmethod
	def verify(
		self,
		hash_value: str | bytes,
		signature_b64: str,
		public_key_pem: str,
		profile: Any,
		signer_name: str,
	) -> CryptoVerificationResult:
		"""Verify signature using the UTF-8 encoded SHA-256 hex digest."""

