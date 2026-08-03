"""Smoke tests for Excel validator imports and construction."""

import unittest
from pathlib import Path

from app.execution_context import ExecutionContext
from config.models import DVEConfig
from crypto.engine import CryptoEngine
from crypto.key_manager import KeyManager
from events.event_bus import EventBus
from services.scan_service import ScanService
from validators.excel_validator import ExcelValidator


class TestExcelValidator(unittest.TestCase):
    """Ensures key validation services are constructible with typed config."""

    def test_services_construct(self) -> None:
        cfg = DVEConfig()
        ctx = ExecutionContext(cfg)
        bus = EventBus()
        scanner = ScanService(ctx, bus)
        key_manager = KeyManager(cfg.excel, Path.cwd())
        validator = ExcelValidator(
            event_bus=bus,
            excel_config=cfg.excel,
            crypto_config=cfg.crypto,
            validation_policy=cfg.validation_policy,
            key_manager=key_manager,
            crypto_engine=CryptoEngine(),
        )
        self.assertIsNotNone(scanner)
        self.assertIsNotNone(validator)


if __name__ == "__main__":
    unittest.main()
