"""Base validator utilities shared by concrete validator implementations."""

from __future__ import annotations

import logging


class BaseValidator:
	"""Provides shared logger and helper behavior for validators."""

	def __init__(self) -> None:
		self.logger = logging.getLogger(self.__class__.__name__)

