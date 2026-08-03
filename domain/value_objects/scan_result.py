"""Value object describing scanner output statistics."""

from dataclasses import dataclass


@dataclass(slots=True)
class ScanResult:
	"""Aggregated scan counts for one execution."""

	files_scanned: int
	folders_visited: int
	skipped_files: int
	skipped_folders: int
	unsupported_files: int

