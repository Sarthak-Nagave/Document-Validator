"""Tests for production Excel hash generation behavior."""

import tempfile
import unittest
from pathlib import Path

import openpyxl

from validators.excel_validator import ExcelValidator


class TestPayloadFramework(unittest.TestCase):
    """Ensures the production Excel hash algorithm is deterministic."""

    def test_generate_hash_from_excel_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workbook_path = Path(tmp_dir) / "sample.xlsx"

            wb = openpyxl.Workbook()
            ws1 = wb.active
            ws1.title = "Sheet1"
            ws1["A1"] = "Value 1"
            ws1["B1"] = "Line 1\nLine 2"

            ws2 = wb.create_sheet("Digital Signature")
            ws2["A2"] = "dummy-signature"
            wb.save(workbook_path)
            wb.close()

            first = ExcelValidator.generate_hash_from_excel(workbook_path)
            second = ExcelValidator.generate_hash_from_excel(workbook_path)
            self.assertEqual(first, second)
            self.assertEqual(len(first), 64)


if __name__ == "__main__":
    unittest.main()
