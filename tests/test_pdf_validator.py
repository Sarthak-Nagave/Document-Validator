"""Smoke tests for PDF validator construction."""

import unittest

from config.models import PDFConfig
from events.event_bus import EventBus
from validators.pdf_validator import PDFValidator


class TestPdfValidator(unittest.TestCase):
    """Ensures PDF validator can be instantiated."""

    def test_constructor(self) -> None:
        validator = PDFValidator(EventBus(), PDFConfig())
        self.assertIsNotNone(validator)


if __name__ == "__main__":
    unittest.main()
