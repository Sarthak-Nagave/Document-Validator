"""Default configuration helpers for DVE."""

from __future__ import annotations

from config.models import DVEConfig


def build_default_config() -> DVEConfig:
	"""Return a default configuration object used as a startup fallback."""
	return DVEConfig()

