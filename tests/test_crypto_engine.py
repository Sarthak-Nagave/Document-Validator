"""Smoke tests for cryptographic engine behavior."""

import unittest

from config.models import CryptoProfile
from crypto.engine import CryptoEngine
from domain.enums.validation_status import ValidationStatus


class TestCryptoEngine(unittest.TestCase):
    """Validates safe failure behavior for malformed signature data."""

    def test_verify_returns_failed_on_invalid_signature(self) -> None:
        engine = CryptoEngine()
        profile = CryptoProfile()
        result = engine.verify(b"data", "not_base64", "invalid", profile, "Signer")
        self.assertEqual(result.verification_status, ValidationStatus.FAILED)


if __name__ == "__main__":
    unittest.main()
