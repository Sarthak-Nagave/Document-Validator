"""Factory for constructing reporting services."""

from __future__ import annotations

from reports.builder import ReportBuilder
from reports.exporter import ReportExporter
from reports.manager import ReportManager


class ReportFactory:
	"""Creates report manager dependencies."""

	@staticmethod
	def create() -> ReportManager:
		"""Create a fully wired report manager."""
		return ReportManager(builder=ReportBuilder(), exporter=ReportExporter())

