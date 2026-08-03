"""Validator interface for document type specific validation services."""

from __future__ import annotations

from abc import ABC, abstractmethod
import logging

from domain.entities.validation_task import ValidationTask
from domain.value_objects.validation_result import ValidationResult


logger = logging.getLogger(__name__)


class IValidator(ABC):
	"""Contract implemented by all concrete validators.

	Implementations must always return a ValidationResult object and handle
	validation errors without crashing the application runtime.
	"""

	@abstractmethod
	def validate(self, task: ValidationTask) -> ValidationResult:
		"""Validate a task and return a normalized result object."""

