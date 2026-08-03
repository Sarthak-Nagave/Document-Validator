"""Public key resolution service for Excel signature verification."""

from __future__ import annotations

from pathlib import Path
from threading import RLock
import logging

from config.models import ExcelConfig


logger = logging.getLogger(__name__)


class KeyManager:
	"""Loads signer-specific PEM public keys from configured key paths."""

	def __init__(self, excel_config: ExcelConfig, root_path: Path) -> None:
		self._excel_config = excel_config
		self._root_path = root_path
		self._lock = RLock()
		self._cache: dict[str, str] = {}
		self._profile_cache: dict[str, str] = {}
		self._normalized_signer_map: dict[str, str] = {}
		self._validate_configuration()

	@staticmethod
	def _normalize_signer_name(name: str) -> str:
		return " ".join((name or "").replace("\r", " ").replace("\n", " ").replace("\t", " ").split()).lower()

	def _validate_configuration(self) -> None:
		"""Validate configured key metadata at startup for fast fail diagnostics."""
		seen_paths: dict[str, str] = {}
		for signer, cfg in self._excel_config.public_keys.items():
			normalized = self._normalize_signer_name(signer)
			if normalized and normalized not in self._normalized_signer_map:
				self._normalized_signer_map[normalized] = signer
			resolved = str((self._root_path / cfg.key_path).resolve())
			if resolved in seen_paths and seen_paths[resolved] != signer:
				logger.warning(
					"Duplicate key path configured for signers %s and %s: %s",
					seen_paths[resolved], signer, resolved
				)
			else:
				seen_paths[resolved] = signer
			if cfg.enabled and not Path(resolved).exists():
				logger.warning("Configured key file missing for signer %s at %s", signer, resolved)
			self._profile_cache[signer] = cfg.profile

	def get_profile_name(self, signer_name: str) -> str:
		"""Return the cryptographic profile associated with the signer."""
		signer_name = signer_name or ""
		canonical = self._normalized_signer_map.get(self._normalize_signer_name(signer_name), signer_name)
		with self._lock:
			if canonical in self._profile_cache:
				return self._profile_cache[canonical]
		cfg = self._excel_config.public_keys.get(canonical)
		profile = cfg.profile if cfg else "default"
		with self._lock:
			self._profile_cache[canonical] = profile
		return profile

	def get_public_key(self, signer_name: str) -> str:
		"""Return signer public key PEM content or an empty string when unavailable."""
		signer_name = signer_name or ""
		canonical = self._normalized_signer_map.get(self._normalize_signer_name(signer_name), signer_name)
		with self._lock:
			if canonical in self._cache:
				return self._cache[canonical]

		cfg = self._excel_config.public_keys.get(canonical)
		if cfg is None:
			logger.warning("No public key configured for signer %s", canonical)
			with self._lock:
				self._cache[canonical] = ""
			return ""
		if not cfg.enabled:
			logger.warning("Public key disabled for signer %s", canonical)
			with self._lock:
				self._cache[canonical] = ""
			return ""

		key_path = (self._root_path / cfg.key_path).resolve()
		if not key_path.exists():
			logger.error("Public key file not found for signer %s at %s", canonical, key_path)
			with self._lock:
				self._cache[canonical] = ""
			return ""

		try:
			key_data = key_path.read_text(encoding="utf-8")
			with self._lock:
				self._cache[canonical] = key_data
			return key_data
		except Exception as exc:
			logger.exception("Failed to read public key for signer %s: %s", canonical, exc)
			with self._lock:
				self._cache[canonical] = ""
			return ""

