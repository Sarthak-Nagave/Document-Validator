"""Report generation interface contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Sequence

from domain.value_objects.validation_result import ValidationResult


class IReportExporter(ABC):
	"""Contract for report exporters writing validation output artifacts."""

	@abstractmethod
	def export(self, results: Sequence[ValidationResult], target_dir: Path) -> Path:
		"""Export results to the target directory and return output file path."""

