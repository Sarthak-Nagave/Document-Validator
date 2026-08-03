"""Rendering helpers for report templates."""

from __future__ import annotations


class ReportRenderer:
	"""Placeholder renderer abstraction kept for layered reporting architecture."""

	def render(self, payload: dict) -> dict:
		"""Return payload unchanged for current renderer strategy."""
		return payload

