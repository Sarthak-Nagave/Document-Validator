"""Factory for resolving document validators by extension."""

from __future__ import annotations

from interfaces.validator import IValidator


class ValidatorFactory:
	"""Simple registry-backed validator factory used by the dispatcher."""

	def __init__(self) -> None:
		self._validators: dict[str, IValidator] = {}

	def register(self, extension: str, validator: IValidator) -> None:
		"""Register a validator for a file extension."""
		self._validators[extension.lower()] = validator

	def get_validator(self, extension: str) -> IValidator | None:
		"""Return a validator for extension or None if unsupported."""
		return self._validators.get(extension.lower())

