"""Bootstrap helpers for initializing logging and runtime environment."""

from __future__ import annotations

from pathlib import Path
import logging

from app.dependency_container import DependencyContainer
from config.config_loader import ConfigLoader


def configure_logging(root_path: Path) -> None:
	"""Configure application logging based on loaded config."""
	config = ConfigLoader(root_path / "config" / "config.json").load()
	log_level = getattr(logging, config.logging.level.upper(), logging.INFO)
	logging.basicConfig(
		level=log_level,
		format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
	)


def bootstrap_container(root_path: Path) -> DependencyContainer:
	"""Create and return the dependency container after runtime bootstrap."""
	configure_logging(root_path)
	logger = logging.getLogger(__name__)
	logger.info("Bootstrapping dependency container from %s", root_path)
	return DependencyContainer(root_path)

