"""Plugin architecture interfaces for optional validator extensions."""

from __future__ import annotations

from abc import ABC, abstractmethod


class IPlugin(ABC):
	"""Contract for plugins that can extend DVE behavior."""

	@property
	@abstractmethod
	def name(self) -> str:
		"""Unique plugin name."""

	@abstractmethod
	def register(self, container) -> None:
		"""Register plugin contributions into the dependency container."""

