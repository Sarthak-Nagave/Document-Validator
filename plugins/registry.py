"""In-memory plugin registry."""

from __future__ import annotations

from plugins.interfaces import IPlugin


class PluginRegistry:
	"""Stores plugins and provides deterministic registration order."""

	def __init__(self) -> None:
		self._plugins: dict[str, IPlugin] = {}

	def add(self, plugin: IPlugin) -> None:
		"""Add a plugin to the registry."""
		self._plugins[plugin.name] = plugin

	def all(self) -> list[IPlugin]:
		"""Return all registered plugins."""
		return [self._plugins[name] for name in sorted(self._plugins.keys())]

