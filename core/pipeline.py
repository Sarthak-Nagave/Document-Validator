"""Validation pipeline abstraction for core processing flow."""

from __future__ import annotations

import logging

from services.validation_orchestrator import ValidationOrchestrator


logger = logging.getLogger(__name__)


class ValidationPipeline:
	"""Encapsulates orchestration to keep engine responsibilities focused."""

	def __init__(self, orchestrator: ValidationOrchestrator) -> None:
		self._orchestrator = orchestrator

	def execute(self, root_path: str):
		"""Execute validation for all discovered tasks."""
		logger.info("Pipeline execution started for %s", root_path)
		results = self._orchestrator.execute(root_path)
		logger.info("Pipeline execution completed with %s results", len(results))
		return results

