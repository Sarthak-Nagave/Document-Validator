"""Validation result value object."""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

from domain.enums.validation_status import ValidationStatus
from domain.enums.severity import Severity

@dataclass
class SignatureValidationResult:
    role: str
    configured_name: str
    detected_certificate_cn: str
    certificate_subject: str
    certificate_issuer: str
    certificate_thumbprint: str
    signing_time: str
    certificate_validity: str
    signature_integrity: str
    validation_status: str
    warning_list: List[str] = field(default_factory=list)
    error_list: List[str] = field(default_factory=list)

@dataclass
class PageValidationResult:
    page_number: int
    page_status: str
    validation_time: float
    required_roles: List[str] = field(default_factory=list)
    detected_roles: List[str] = field(default_factory=list)
    prepared_result: str = "NOT_FOUND"
    verified_result: str = "NOT_FOUND"
    approved_result: str = "NOT_FOUND"
    certificate_details: List[Dict[str, Any]] = field(default_factory=list)
    warning_list: List[str] = field(default_factory=list)
    error_list: List[str] = field(default_factory=list)
    signature_results: List[SignatureValidationResult] = field(default_factory=list)

@dataclass
class PDFValidationResult:
    file_name: str
    total_pages: int
    pages_passed: int
    pages_failed: int
    required_signatures: int
    detected_signatures: int
    missing_signatures: int
    unexpected_signatures: int
    duplicate_signatures: int
    overall_status: str
    execution_time: float
    warning_list: List[str] = field(default_factory=list)
    error_list: List[str] = field(default_factory=list)

@dataclass
class ValidationIssue:
    severity: Severity
    message: str

@dataclass
class CryptoVerificationResult:
    algorithm: str
    hash_algorithm: str
    padding: str
    verification_status: ValidationStatus
    reason: str
    execution_time: float
    warnings: List[ValidationIssue] = field(default_factory=list)
    errors: List[ValidationIssue] = field(default_factory=list)
    public_key_used: str = ""
    verification_profile: str = ""
    expected_payload_sha256: str = ""
    generated_payload_sha256: str = ""
    payload_length: int = 0
    signature_length: int = 0
    diagnostics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExcelValidationResult:
    workbook_name: str
    sheet1_signer: str
    approved_by_signer: str
    signer_match: bool
    public_key: str
    crypto_result: Optional[CryptoVerificationResult] = None
    workbook_status: ValidationStatus = ValidationStatus.NOT_IMPLEMENTED
    warnings: List[ValidationIssue] = field(default_factory=list)
    errors: List[ValidationIssue] = field(default_factory=list)
    execution_time: float = 0.0
    signature_version: str = ""
    workbook_identifier: str = ""
    approval_date: str = ""
    payload_sha256: str = ""
    expected_payload_sha256: str = ""
    payload_length: int = 0
    signature_length: int = 0
    payload_strategy: str = ""
    payload_status: str = ""

@dataclass
class TimelineEvent:
    event: str
    timestamp: str

@dataclass
class ValidationResult:
    task_id: uuid.UUID
    validator_name: str
    root_group: str = ""
    execution_time: float = 0.0
    status: ValidationStatus = ValidationStatus.NOT_IMPLEMENTED
    reason: str = "Validation module not implemented yet."
    is_valid: bool = False
    warning_list: List[str] = field(default_factory=list)
    error_list: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    task: Any = None
    
    # Audit Trail & Fingerprinting
    audit_id: uuid.UUID = field(default_factory=uuid.uuid4)
    execution_id: str = ""
    validation_policy: str = ""
    app_version: str = ""
    config_version: str = ""
    validator_version: str = ""
    verification_profile: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    document_fingerprint: str = ""
    timeline: List[TimelineEvent] = field(default_factory=list)
    
    # Specific results
    pdf_result: Optional[PDFValidationResult] = None
    excel_result: Optional[ExcelValidationResult] = None

    def add_timeline_event(self, event: str):
        self.timeline.append(TimelineEvent(event=event, timestamp=datetime.utcnow().isoformat()))
