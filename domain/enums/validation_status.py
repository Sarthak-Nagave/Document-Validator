"""Validation status values used across the DVE pipeline."""

from enum import Enum
import logging


logger = logging.getLogger(__name__)


class ValidationStatus(str, Enum):
	"""Canonical status outcomes for validation operations."""

	SUCCESS = "SUCCESS"
	FAILED = "FAILED"
	WARNING = "WARNING"
	SKIPPED = "SKIPPED"
	ERROR = "ERROR"
	NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
	PAYLOAD_BUILDER_NOT_IMPLEMENTED = "PAYLOAD_BUILDER_NOT_IMPLEMENTED"

	@classmethod
	def from_value(cls, value: str) -> "ValidationStatus":
		"""Create a status from a string value using case-insensitive matching."""
		normalized = value.strip().upper()
		try:
			status = cls(normalized)
			logger.debug("Mapped status string '%s' to enum %s", value, status)
			return status
		except ValueError as exc:
			logger.error("Unknown validation status '%s'", value)
			raise ValueError(f"Unknown validation status: {value}") from exc

	def is_terminal(self) -> bool:
		"""Return True when status indicates a terminal validation outcome."""
		return self in {self.SUCCESS, self.FAILED, self.WARNING, self.SKIPPED, self.ERROR}

