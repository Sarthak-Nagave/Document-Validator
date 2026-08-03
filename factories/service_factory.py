"""Factory utilities for assembling high-level services."""

from __future__ import annotations

from pathlib import Path

from reports.manager import ReportManager
from services.report_service import ReportService


class ServiceFactory:
	"""Constructs service instances while preserving dependency inversion."""

	@staticmethod
	def create_report_service(report_manager: ReportManager, output_root: Path) -> ReportService:
		"""Create report service with output/report target folder."""
		return ReportService(report_manager=report_manager, output_dir=output_root / "reports")

