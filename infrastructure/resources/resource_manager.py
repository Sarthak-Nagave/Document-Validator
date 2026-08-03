"""Resource manager for resolving packaged/static file paths."""

from __future__ import annotations

from pathlib import Path


class ResourceManager:
	"""Resolves application resource paths in source and packaged modes."""

	def __init__(self, root_path: Path) -> None:
		self._root_path = root_path

	def resolve(self, relative_path: str) -> Path:
		"""Resolve a resource path from project root."""
		return (self._root_path / relative_path).resolve()

