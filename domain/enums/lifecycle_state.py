"""Lifecycle states used by the core engine runtime."""

from enum import Enum


class LifecycleState(str, Enum):
	"""Represents high-level engine lifecycle states."""

	IDLE = "IDLE"
	STARTING = "STARTING"
	RUNNING = "RUNNING"
	COMPLETED = "COMPLETED"
	FAILED = "FAILED"

