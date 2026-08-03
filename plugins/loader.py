"""Plugin loader for optional runtime extensions."""

from __future__ import annotations

from pathlib import Path
import importlib.util
import logging

from plugins.interfaces import IPlugin
from plugins.registry import PluginRegistry


logger = logging.getLogger(__name__)


class PluginLoader:
	"""Loads plugin modules from filesystem and registers plugin instances."""

	def __init__(self, plugins_dir: Path, registry: PluginRegistry) -> None:
		self._plugins_dir = plugins_dir
		self._registry = registry

	def load(self) -> None:
		"""Load all file-based plugins and register discovered instances."""
		if not self._plugins_dir.exists():
			return
		for file in sorted(self._plugins_dir.glob("*.py")):
			if file.name.startswith("_"):
				continue
			spec = importlib.util.spec_from_file_location(file.stem, file)
			if spec is None or spec.loader is None:
				continue
			module = importlib.util.module_from_spec(spec)
			try:
				spec.loader.exec_module(module)
			except Exception as exc:
				logger.exception("Failed to load plugin module %s: %s", file, exc)
				continue
			plugin = getattr(module, "plugin", None)
			if isinstance(plugin, IPlugin):
				self._registry.add(plugin)

