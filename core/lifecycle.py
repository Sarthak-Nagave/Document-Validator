"""Lifecycle manager for engine execution state transitions."""

from __future__ import annotations

import logging

from domain.enums.lifecycle_state import LifecycleState


logger = logging.getLogger(__name__)


class LifecycleManager:
	"""Tracks and validates high-level engine lifecycle transitions."""

	def __init__(self) -> None:
		self._state = LifecycleState.IDLE

	@property
	def state(self) -> LifecycleState:
		"""Return current lifecycle state."""
		return self._state

	def start(self) -> None:
		"""Transition lifecycle to running sequence."""
		self._state = LifecycleState.STARTING
		self._state = LifecycleState.RUNNING
		logger.info("Lifecycle transitioned to %s", self._state)

	def complete(self) -> None:
		"""Transition lifecycle to completed state."""
		self._state = LifecycleState.COMPLETED
		logger.info("Lifecycle transitioned to %s", self._state)

	def fail(self) -> None:
		"""Transition lifecycle to failed state."""
		self._state = LifecycleState.FAILED
		logger.error("Lifecycle transitioned to %s", self._state)

