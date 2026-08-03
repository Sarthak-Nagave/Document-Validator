"""Value object describing generated report artifact paths."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class ReportResult:
	"""Tracks created report output files for one run."""

	generated_files: list[str] = field(default_factory=list)

