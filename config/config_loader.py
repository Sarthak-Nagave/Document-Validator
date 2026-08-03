"""Load and parse DVE JSON configuration into typed dataclasses."""

from __future__ import annotations

from pathlib import Path
import json
import logging

from config.defaults import build_default_config
from config.models import DVEConfig


logger = logging.getLogger(__name__)


class ConfigLoader:
	"""Configuration loader with graceful fallback to defaults."""

	def __init__(self, config_path: Path) -> None:
		self._config_path = config_path

	def load(self) -> DVEConfig:
		"""Load configuration from disk or return defaults when unavailable."""
		if not self._config_path.exists():
			logger.warning("Config file not found at %s, using defaults", self._config_path)
			return build_default_config()

		try:
			payload = json.loads(self._config_path.read_text(encoding="utf-8"))
			config = DVEConfig.from_dict(payload)
			logger.info("Loaded configuration from %s", self._config_path)
			return config
		except Exception as exc:
			logger.exception("Failed to load config %s: %s", self._config_path, exc)
			return build_default_config()

