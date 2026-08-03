"""Application-level in-memory state registry for runtime status."""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
import logging


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AppState:
	"""Mutable runtime state values for UI and orchestration signaling."""

	current_folder: str = ""
	running: bool = False
	last_error: str = ""


class StateManager:
	"""Provides controlled updates and reads for app runtime state."""

	def __init__(self) -> None:
		self._state = AppState()
		self._lock = RLock()

	@property
	def state(self) -> AppState:
		"""Expose current app state object."""
		with self._lock:
			return AppState(
				current_folder=self._state.current_folder,
				running=self._state.running,
				last_error=self._state.last_error,
			)

	def start(self, folder: str) -> None:
		"""Mark state as running for a given folder."""
		with self._lock:
			self._state.current_folder = folder
			self._state.running = True
			self._state.last_error = ""
		logger.info("StateManager started for folder %s", folder)

	def stop(self) -> None:
		"""Mark state as idle."""
		with self._lock:
			self._state.running = False
		logger.info("StateManager stopped")

	def fail(self, message: str) -> None:
		"""Record a runtime error."""
		with self._lock:
			self._state.last_error = message
			self._state.running = False
		logger.error("StateManager failure: %s", message)

