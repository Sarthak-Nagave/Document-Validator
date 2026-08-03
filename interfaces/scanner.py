"""Scanner interface for document discovery."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Generator
import logging

from domain.entities.validation_task import ValidationTask


logger = logging.getLogger(__name__)


class IScanner(ABC):
	"""Contract for filesystem scanners that produce validation tasks.

	Implementations should stream task creation so large folder trees can be
	processed without loading all tasks into memory.
	"""

	@abstractmethod
	def scan(self, root_path: str) -> Generator[ValidationTask, None, None]:
		"""Yield validation tasks for the provided root path."""

