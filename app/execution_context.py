"""Execution context state used by scanning and validation orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field

from config.models import DVEConfig


@dataclass(slots=True)
class RuntimeMetrics:
	"""Mutable counters for one validation cycle."""

	folders_visited: int = 0
	files_visited: int = 0
	files_scanned: int = 0
	skipped_folders: int = 0
	skipped_files: int = 0
	unsupported_files: int = 0
	validation_tasks_created: int = 0
	pdf_files: int = 0
	excel_files: int = 0
	errors: int = 0


@dataclass(slots=True)
class ExecutionContext:
	"""Runtime context containing immutable configuration and mutable metrics."""

	config: DVEConfig
	metrics: RuntimeMetrics = field(default_factory=RuntimeMetrics)

