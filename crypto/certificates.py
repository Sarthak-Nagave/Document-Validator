"""Certificate helper utilities for signature diagnostics."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CertificateInfo:
	"""Normalized certificate metadata used in reports and diagnostics."""

	subject: str
	issuer: str
	thumbprint: str

