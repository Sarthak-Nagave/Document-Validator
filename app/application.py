"""Application service facade for DVE runtime operations."""

from __future__ import annotations

from pathlib import Path
import logging

from app.dependency_container import DependencyContainer
from app.state_manager import StateManager


logger = logging.getLogger(__name__)

class Application:
	"""Coordinates application-level operations backed by the dependency container."""

	def __init__(self, root_path: Path) -> None:
		self.container = DependencyContainer(root_path)
		self.state_manager = StateManager()

	def run_validation(self, root_folder: str):
		"""Run validation cycle through the configured core engine."""
		self.state_manager.start(root_folder)
		try:
			result = self.container.engine.run(root_folder)
			self.state_manager.stop()
			return result
		except Exception as exc:
			logger.exception("Validation run failed for folder %s", root_folder)
			self.state_manager.fail(str(exc))
			raise

