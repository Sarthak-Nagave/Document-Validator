"""Configuration datamodels for the Document Validation Engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AppConfig:
	"""Application identity settings."""

	name: str = "DVE"


@dataclass(slots=True)
class ScanningConfig:
	"""Filesystem scanning configuration."""

	supported_extensions: list[str] = field(default_factory=lambda: [".pdf", ".xlsx"])
	ignored_folders: list[str] = field(default_factory=list)
	ignored_extensions: list[str] = field(default_factory=list)
	ignore_hidden: bool = True


@dataclass(slots=True)
class LoggingConfig:
	"""Logging settings."""

	level: str = "INFO"


@dataclass(slots=True)
class ValidationPolicyLevel:
	"""Policy thresholds for validation rule handling."""

	missing_signature: str = "FAIL"
	invalid_signature: str = "FAIL"
	unknown_signer: str = "FAIL"
	missing_public_key: str = "FAIL"


@dataclass(slots=True)
class ValidationPolicyConfig:
	"""Policy configuration with strict and relaxed profiles."""

	default: str = "strict"
	strict: ValidationPolicyLevel = field(default_factory=ValidationPolicyLevel)
	relaxed: ValidationPolicyLevel = field(default_factory=ValidationPolicyLevel)


@dataclass(slots=True)
class CryptoProfile:
	"""Cryptographic profile used for signature verification."""

	algorithm: str = "RSA"
	hash: str = "SHA256"
	padding: str = "PKCS1v15"


@dataclass(slots=True)
class CryptoConfig:
	"""Collection of cryptographic profiles."""

	profiles: dict[str, CryptoProfile] = field(default_factory=lambda: {"default": CryptoProfile()})


@dataclass(slots=True)
class PDFValidationConfig:
	"""Required signer map for PDF documents."""

	required_signers: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class PDFConfig:
	"""PDF validation configuration group."""

	validation: PDFValidationConfig = field(default_factory=PDFValidationConfig)


@dataclass(slots=True)
class PublicKeyConfig:
	"""Excel signer public key configuration entry."""

	display_name: str
	enabled: bool
	profile: str
	key_path: str


@dataclass(slots=True)
class ExcelConfig:
	"""Excel validation configuration group."""

	public_keys: dict[str, PublicKeyConfig] = field(default_factory=dict)


@dataclass(slots=True)
class DVEConfig:
	"""Root configuration model for DVE."""

	schema_version: str = "1.0.0"
	application_version: str = "1.0.0"
	app: AppConfig = field(default_factory=AppConfig)
	scanning: ScanningConfig = field(default_factory=ScanningConfig)
	logging: LoggingConfig = field(default_factory=LoggingConfig)
	validation_policy: ValidationPolicyConfig = field(default_factory=ValidationPolicyConfig)
	crypto: CryptoConfig = field(default_factory=CryptoConfig)
	pdf: PDFConfig = field(default_factory=PDFConfig)
	excel: ExcelConfig = field(default_factory=ExcelConfig)

	@classmethod
	def from_dict(cls, payload: dict[str, Any]) -> "DVEConfig":
		"""Create a strongly-typed configuration object from a JSON dictionary."""
		app = AppConfig(**payload.get("app", {}))
		scanning = ScanningConfig(**payload.get("scanning", {}))
		logging_cfg = LoggingConfig(**payload.get("logging", {}))

		policy_data = payload.get("validation_policy", {})
		strict = ValidationPolicyLevel(**policy_data.get("strict", {}))
		relaxed = ValidationPolicyLevel(**policy_data.get("relaxed", {}))
		policy = ValidationPolicyConfig(
			default=policy_data.get("default", "strict"),
			strict=strict,
			relaxed=relaxed,
		)

		crypto_profiles_data = payload.get("crypto", {}).get("profiles", {})
		crypto_profiles = {
			name: CryptoProfile(**data) for name, data in crypto_profiles_data.items()
		}
		crypto = CryptoConfig(profiles=crypto_profiles or {"default": CryptoProfile()})

		pdf_required = payload.get("pdf", {}).get("validation", {}).get("required_signers", {})
		pdf = PDFConfig(validation=PDFValidationConfig(required_signers=pdf_required))

		public_keys_data = payload.get("excel", {}).get("public_keys", {})
		excel_keys = {
			name: PublicKeyConfig(
				display_name=data.get("display_name", name),
				enabled=bool(data.get("enabled", True)),
				profile=data.get("profile", "default"),
				key_path=data.get("key_path", ""),
			)
			for name, data in public_keys_data.items()
		}
		excel = ExcelConfig(public_keys=excel_keys)

		return cls(
			schema_version=payload.get("schema_version", "1.0.0"),
			application_version=payload.get("application_version", "1.0.0"),
			app=app,
			scanning=scanning,
			logging=logging_cfg,
			validation_policy=policy,
			crypto=crypto,
			pdf=pdf,
			excel=excel,
		)

