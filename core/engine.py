"""Core execution engine that drives scan, validation and reporting."""

from __future__ import annotations

import logging

from core.lifecycle import LifecycleManager
from core.pipeline import ValidationPipeline
from services.report_service import ReportService


logger = logging.getLogger(__name__)


class CoreEngine:
	"""Top-level application service for one validation run."""

	def __init__(
		self,
		pipeline: ValidationPipeline,
		report_service: ReportService,
		lifecycle: LifecycleManager,
	) -> None:
		self._pipeline = pipeline
		self._report_service = report_service
		self._lifecycle = lifecycle

	def run(self, root_path: str) -> list:
		"""Run validation and report generation for a target folder."""
		logger.info("Engine started for %s", root_path)
		self._lifecycle.start()
		try:
			results = self._pipeline.execute(root_path)
			self._report_service.generate(results)
			self._lifecycle.complete()
			logger.info("Engine finished for %s", root_path)
			return results
		except Exception:
			self._lifecycle.fail()
			logger.exception("Engine failed for %s", root_path)
			raise

