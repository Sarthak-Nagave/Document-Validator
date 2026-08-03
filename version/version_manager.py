"""Version management helpers for the DVE runtime."""

from version.build_info import BUILD_NAME, BUILD_VERSION


class VersionManager:
	"""Provides canonical version strings used by GUI and reports."""

	@staticmethod
	def get_display_version() -> str:
		"""Return user-facing application version label."""
		return f"{BUILD_NAME} v{BUILD_VERSION}"

