"""Domain entity for configured signer metadata."""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Signer:
	"""Represents a signer definition used by PDF/Excel validation logic."""

	role: str
	display_name: str
	enabled: bool = True
	profile: str = "default"
	key_path: str = ""

