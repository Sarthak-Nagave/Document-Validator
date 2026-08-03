"""Configuration service for accessing loaded DVE settings."""

from __future__ import annotations

from config.models import DVEConfig


class ConfigurationService:
	"""Read-only facade over typed configuration data."""

	def __init__(self, config: DVEConfig) -> None:
		self._config = config

	@property
	def config(self) -> DVEConfig:
		"""Return the loaded configuration object."""
		return self._config

