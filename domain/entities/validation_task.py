"""Domain entity representing a single document validation task."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import logging
import time
import uuid


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ValidationTask:
	"""Immutable-like task descriptor produced by scanning and consumed by validators.

	The task encapsulates file metadata and execution identifiers so validators
	can operate deterministically and emit traceable results.
	"""

	file_path: Path
	relative_path: str
	file_name: str
	extension: str
	root_group: str
	file_size: int
	created_time: float
	modified_time: float
	task_id: uuid.UUID = field(default_factory=uuid.uuid4)
	execution_id: uuid.UUID = field(default_factory=uuid.uuid4)
	discovered_at: float = field(default_factory=time.time)
	source: Optional[str] = None

	def __post_init__(self) -> None:
		"""Normalize key values and validate required fields."""
		if not self.file_name:
			raise ValueError("ValidationTask.file_name cannot be empty")
		if not self.extension:
			raise ValueError("ValidationTask.extension cannot be empty")

		self.extension = self.extension.lower()
		logger.debug(
			"Created ValidationTask id=%s file=%s extension=%s root_group=%s",
			self.task_id,
			self.file_name,
			self.extension,
			self.root_group,
		)

