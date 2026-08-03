"""Cryptographic verification engine for Excel signature validation."""

from __future__ import annotations

from base64 import b64decode
import time
import logging
import hashlib

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key

from config.models import CryptoProfile
from domain.enums.severity import Severity
from domain.enums.validation_status import ValidationStatus
from domain.value_objects.validation_result import (
	CryptoVerificationResult,
	ValidationIssue,
)


logger = logging.getLogger(__name__)


class CryptoEngine:
	"""Verifies detached signatures against generated payload bytes."""

	@staticmethod
	def _extract_expected_payload_sha256(signature: bytes, public_key) -> str:
		"""Extract expected SHA-256 digest from RSA PKCS#1 v1.5 signature block."""
		try:
			nums = public_key.public_numbers()
			n = nums.n
			e = nums.e
			key_size_bytes = (n.bit_length() + 7) // 8
			em = pow(int.from_bytes(signature, "big"), e, n).to_bytes(key_size_bytes, "big")
			sep_idx = em.find(b"\x00", 2)
			if sep_idx < 0:
				return ""
			digest_info = em[sep_idx + 1 :]
			sha256_prefix = bytes.fromhex("3031300d060960864801650304020105000420")
			if not digest_info.startswith(sha256_prefix):
				return ""
			expected = digest_info[len(sha256_prefix) : len(sha256_prefix) + 32]
			if len(expected) != 32:
				return ""
			return expected.hex()
		except Exception:
			return ""

	def verify(
		self,
		hash_value: str | bytes,
		signature_b64: str,
		public_key_pem: str,
		profile: CryptoProfile,
		signer_name: str,
		payload_strategy: str = "",
		suppress_log: bool = False,
	) -> CryptoVerificationResult:
		"""Verify a base64 signature using the UTF-8 encoded SHA-256 hex digest."""
		start = time.time()
		hash_text = hash_value.decode("utf-8") if isinstance(hash_value, bytes) else str(hash_value)

		result = CryptoVerificationResult(
			algorithm=profile.algorithm,
			hash_algorithm=profile.hash,
			padding=profile.padding,
			verification_status=ValidationStatus.FAILED,
			reason="Verification not completed",
			execution_time=0.0,
			public_key_used=signer_name,
			verification_profile=profile.algorithm,
			generated_payload_sha256=hash_text,
			payload_length=len(hash_text.encode("utf-8")),
			diagnostics={"payload_strategy": payload_strategy},
		)

		try:
			signature = b64decode(signature_b64)
			pub_key = load_pem_public_key(public_key_pem.encode("utf-8"))
			result.signature_length = len(signature)
			result.expected_payload_sha256 = self._extract_expected_payload_sha256(signature, pub_key)

			hash_algo = hashes.SHA256() if profile.hash.upper() == "SHA256" else hashes.SHA256()
			pad = (
				padding.PKCS1v15()
				if profile.padding.upper() == "PKCS1V15"
				else padding.PKCS1v15()
			)

			pub_key.verify(signature, hash_text.encode("utf-8"), pad, hash_algo)
			result.verification_status = ValidationStatus.SUCCESS
			result.reason = "Signature verified successfully"
		except Exception as exc:
			err_text = str(exc).strip() or "signature mismatch"
			if suppress_log:
				logger.debug("Crypto verification failed for signer %s: %s", signer_name, err_text)
			else:
				logger.warning("Crypto verification failed for signer %s: %s", signer_name, err_text)
			result.verification_status = ValidationStatus.FAILED
			reason = f"Signature verification failed: {err_text}"
			if result.expected_payload_sha256:
				reason = (
					f"{reason} | expected_sha256={result.expected_payload_sha256} "
					f"generated_sha256={result.generated_payload_sha256}"
				)
			result.reason = reason
			result.errors.append(
				ValidationIssue(severity=Severity.ERROR, message=result.reason)
			)
		finally:
			result.execution_time = time.time() - start

		return result

