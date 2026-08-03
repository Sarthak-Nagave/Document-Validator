"""Tests for key manager fallback behavior."""

import unittest
from pathlib import Path

from config.models import ExcelConfig
from crypto.key_manager import KeyManager


class TestKeyManager(unittest.TestCase):
    """Verifies missing-key scenarios are handled gracefully."""

    def test_unknown_signer_returns_empty_key(self) -> None:
        manager = KeyManager(ExcelConfig(), Path.cwd())
        self.assertEqual(manager.get_public_key("Unknown"), "")


if __name__ == "__main__":
    unittest.main()
