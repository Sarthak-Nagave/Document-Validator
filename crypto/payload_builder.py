"""Payload builder interfaces for workbook canonicalization."""

from __future__ import annotations

from typing import Protocol


class IPayloadBuilder(Protocol):
	"""Protocol for payload builders used in signature verification."""

	def build_payload(self, workbook) -> bytes:
		"""Build deterministic bytes for signature verification."""

