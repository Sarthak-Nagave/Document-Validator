"""Value object for scan summary information."""

from dataclasses import dataclass


@dataclass(slots=True)
class ScanSummary:
	"""Human-readable summary over scanning and discovery metrics."""

	total_files: int
	total_supported: int
	total_unsupported: int

