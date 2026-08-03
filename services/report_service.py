"""Report service for exporting validation outputs."""

from __future__ import annotations

from pathlib import Path
import logging

from domain.value_objects.validation_result import ValidationResult
from reports.manager import ReportManager


logger = logging.getLogger(__name__)


class ReportService:
	"""Facade responsible for writing report files for a completed run."""

	def __init__(self, report_manager: ReportManager, output_dir: Path) -> None:
		self._manager = report_manager
		self._output_dir = output_dir

	def generate(self, results: list[ValidationResult]) -> list[Path]:
		"""Generate all configured report formats and return created paths."""
		created = self._manager.export_all(results, self._output_dir)
		logger.info("Generated %s report artifacts", len(created))
		return created

