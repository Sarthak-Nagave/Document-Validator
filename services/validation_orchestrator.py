"""Validation orchestration service coordinating scan and dispatch flows."""

from __future__ import annotations

from collections.abc import Iterable
import logging

from core.dispatcher import Dispatcher
from interfaces.scanner import IScanner
from domain.value_objects.validation_result import ValidationResult


logger = logging.getLogger(__name__)


class ValidationOrchestrator:
	"""Runs the validation cycle and accumulates normalized results."""

	def __init__(self, scanner: IScanner, dispatcher: Dispatcher) -> None:
		self._scanner = scanner
		self._dispatcher = dispatcher

	def execute(self, root_path: str) -> list[ValidationResult]:
		"""Execute scan-and-validate flow for all discovered tasks."""
		results: list[ValidationResult] = []
		for task in self._scanner.scan(root_path):
			result = self._dispatcher.dispatch(task)
			if result is None:
				continue
			result.task = task
			results.append(result)
		logger.info("Validation cycle completed with %s results", len(results))
		return results

