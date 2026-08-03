"""Report manager coordinating report payload build and exports."""

from __future__ import annotations

from pathlib import Path

from domain.value_objects.validation_result import ValidationResult
from reports.builder import ReportBuilder
from reports.exporter import ReportExporter


class ReportManager:
	"""Coordinates all reporting artifact generation."""

	def __init__(self, builder: ReportBuilder, exporter: ReportExporter) -> None:
		self._builder = builder
		self._exporter = exporter

	def export_all(self, results: list[ValidationResult], target_dir: Path) -> list[Path]:
		"""Generate JSON, HTML and XLSX reports for a completed run."""
		target_dir.mkdir(parents=True, exist_ok=True)
		payload = self._builder.build(results)
		return [
			self._exporter.export_json(payload, target_dir),
			self._exporter.export_html(payload, target_dir),
			self._exporter.export_xlsx(payload, target_dir),
		]

