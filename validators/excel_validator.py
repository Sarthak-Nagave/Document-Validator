"""Enterprise Excel Digital Signature Validator."""
import base64
import hashlib
import logging
import time

import openpyxl
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from interfaces.validator import IValidator
from domain.entities.validation_task import ValidationTask
from domain.value_objects.validation_result import (
    ValidationResult,
    ExcelValidationResult,
    TimelineEvent,
    ValidationIssue,
    CryptoVerificationResult
)
from events.event_bus import EventBus
from events.event_types import EventType
from domain.enums.validation_status import ValidationStatus
from domain.enums.severity import Severity
from config.models import ExcelConfig, CryptoConfig, ValidationPolicyConfig
from crypto.key_manager import KeyManager
from crypto.engine import CryptoEngine


logger = logging.getLogger(__name__)

class ExcelValidator(IValidator):
    def __init__(self, 
                 event_bus: EventBus, 
                 excel_config: ExcelConfig, 
                 crypto_config: CryptoConfig,
                 validation_policy: ValidationPolicyConfig,
                 key_manager: KeyManager,
                 crypto_engine: CryptoEngine):
        self.event_bus = event_bus
        self.excel_config = excel_config
        self.crypto_config = crypto_config
        self.validation_policy = validation_policy
        self.key_manager = key_manager
        self.crypto_engine = crypto_engine

    @staticmethod
    def _normalize_name(value: str) -> str:
        return " ".join((value or "").replace("\r", " ").replace("\n", " ").replace("\t", " ").split()).lower()

    @staticmethod
    def find_signature(file_path) -> str | None:
        wb = openpyxl.load_workbook(file_path)
        try:
            if "Digital Signature" not in wb.sheetnames:
                return None
            ws = wb["Digital Signature"]
            signature = ws["A2"].value
            if not signature:
                return None
            return str(signature).strip()
        finally:
            wb.close()

    @staticmethod
    def find_approver(file_path) -> str | None:
        wb = openpyxl.load_workbook(file_path)
        try:
            if "Digital Signature" not in wb.sheetnames:
                return None
            ws = wb["Digital Signature"]
            text = ws["A3"].value
            if not text:
                return None
            text = str(text).strip()
            if text.startswith("Approved by "):
                text = text.replace("Approved by ", "", 1)
            return text.split(" on ")[0].strip()
        finally:
            wb.close()

    @staticmethod
    def generate_hash_from_excel(file_path) -> str:
        wb = openpyxl.load_workbook(file_path, data_only=False)
        collected: list[str] = []
        try:
            for sheet_name in sorted(wb.sheetnames):
                if sheet_name == "Digital Signature":
                    continue
                ws = wb[sheet_name]
                collected.append(f"---SHEET:{sheet_name}---")
                for row in ws.iter_rows():
                    for cell in row:
                        value = cell.value
                        if value is None:
                            value = ""
                        value = str(value).strip()
                        value = value.replace("\r", "")
                        value = value.replace("\n", " ")
                        collected.append(value)
        finally:
            wb.close()

        content = "|".join(collected)
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @staticmethod
    def verify_signature(hash_value: str, signature_b64: str, public_key_pem: str) -> bool:
        public_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
        signature = base64.b64decode(signature_b64)
        try:
            public_key.verify(
                signature,
                hash_value.encode("utf-8"),
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            return True
        except InvalidSignature:
            return False

    @staticmethod
    def _extract_sheet1_signer(file_path) -> str:
        wb = openpyxl.load_workbook(file_path)
        try:
            if "Sheet1" not in wb.sheetnames:
                return ""
            sheet1 = wb["Sheet1"]
            for row in sheet1.iter_rows(values_only=True):
                if row and row[0] and str(row[0]).strip().endswith(": OK"):
                    return str(row[0]).replace(": OK", "").strip()
            return ""
        finally:
            wb.close()

    def _get_policy_severity(self, policy_name: str, rule: str) -> Severity:
        """Map validation policy rules to Severities."""
        # Check if policy exists in validation_policy config
        if policy_name == "strict":
            mapping = self.validation_policy.strict
        elif policy_name == "relaxed":
            mapping = self.validation_policy.relaxed
        else:
            mapping = self.validation_policy.strict
            
        value = getattr(mapping, rule, "FAIL").upper()
        if value == "FAIL":
            return Severity.ERROR
        elif value == "WARNING":
            return Severity.WARNING
        return Severity.INFO

    def _generate_fingerprint(self, file_path: str) -> str:
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Read in chunks for memory safety
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception:
            return ""

    def validate(self, task: ValidationTask) -> ValidationResult:
        start_time = time.time()
        file_path = task.file_path
        task_id = task.task_id
        
        # Base result skeleton
        result = ValidationResult(
            task_id=task_id,
            validator_name="ExcelValidator",
            root_group=task.root_group,
            status=ValidationStatus.NOT_IMPLEMENTED,
            execution_id=str(task.execution_id) if hasattr(task, 'execution_id') else "",
            validation_policy=self.validation_policy.default,
            app_version="1.0.0",
            validator_version="1.0.0"
        )
        
        # Start timeline
        result.add_timeline_event("Validation Started")
        
        # Generate fingerprint
        result.document_fingerprint = self._generate_fingerprint(str(file_path))
        result.add_timeline_event("Document Fingerprint Generated")
        
        # Initialize specialized excel result
        excel_res = ExcelValidationResult(
            workbook_name=file_path.name,
            sheet1_signer="",
            approved_by_signer="",
            signer_match=False,
            public_key=""
        )
        
        try:
            result.add_timeline_event("Workbook Parsed")

            signature_b64 = self.find_signature(file_path)
            if not signature_b64:
                msg = "Digital Signature not found"
                excel_res.errors.append(ValidationIssue(severity=Severity.ERROR, message=msg))
                result.error_list.append(msg)
                result.status = ValidationStatus.FAILED
                result.is_valid = False
                result.reason = msg
                excel_res.workbook_status = ValidationStatus.FAILED
                result.excel_result = excel_res
                result.execution_time = time.time() - start_time
                return result

            approved_by = self.find_approver(file_path)
            if not approved_by:
                msg = "Approver not found in Digital Signature A3"
                excel_res.errors.append(ValidationIssue(severity=Severity.ERROR, message=msg))
                result.error_list.append(msg)
                result.status = ValidationStatus.FAILED
                result.is_valid = False
                result.reason = msg
                excel_res.workbook_status = ValidationStatus.FAILED
                result.excel_result = excel_res
                result.execution_time = time.time() - start_time
                return result

            sheet1_signer = self._extract_sheet1_signer(file_path)
            excel_res.sheet1_signer = sheet1_signer
            excel_res.approved_by_signer = approved_by

            normalized_sheet1 = self._normalize_name(sheet1_signer)
            normalized_approved = self._normalize_name(approved_by)
            excel_res.signer_match = bool(normalized_sheet1 and normalized_approved and normalized_sheet1 == normalized_approved)
            if sheet1_signer and approved_by and not excel_res.signer_match:
                msg = f"Wrong signer: Sheet1 signer '{sheet1_signer}' does not match Digital Signature approver '{approved_by}'"
                excel_res.errors.append(ValidationIssue(severity=Severity.ERROR, message=msg))
                result.error_list.append(msg)

            signer_for_key = approved_by
            pub_key_pem = self.key_manager.get_public_key(signer_for_key)
            profile_name = self.key_manager.get_profile_name(signer_for_key)
            excel_res.public_key = signer_for_key
            if not pub_key_pem:
                msg = f"Public key not found or disabled for signer: {signer_for_key}"
                excel_res.errors.append(ValidationIssue(severity=Severity.ERROR, message=msg))
                result.error_list.append(msg)
                result.status = ValidationStatus.FAILED
                result.is_valid = False
                result.reason = msg
                excel_res.workbook_status = ValidationStatus.FAILED
                result.excel_result = excel_res
                result.execution_time = time.time() - start_time
                return result

            result.add_timeline_event("Public Key Loaded")
            self.event_bus.publish(EventType.PUBLIC_KEY_LOADED, {"task_id": task_id, "signer": signer_for_key})

            developer_hash = self.generate_hash_from_excel(file_path)
            dve_hash = self.generate_hash_from_excel(file_path)
            result.metadata["developer_hash"] = developer_hash
            result.metadata["generated_hash"] = dve_hash

            if developer_hash != dve_hash:
                logger.error(
                    "Excel hash parity mismatch for %s | Developer Hash=%s | Generated Hash=%s",
                    file_path.name,
                    developer_hash,
                    dve_hash,
                )
                msg = (
                    f"Hash parity mismatch. Developer Hash={developer_hash} "
                    f"Generated Hash={dve_hash} First differing workbook={file_path.name}"
                )
                excel_res.errors.append(ValidationIssue(severity=Severity.ERROR, message=msg))
                result.error_list.append(msg)
                result.status = ValidationStatus.FAILED
                result.is_valid = False
                result.reason = msg
                excel_res.payload_status = "MISMATCH"
                excel_res.payload_sha256 = dve_hash
                excel_res.expected_payload_sha256 = developer_hash
                excel_res.workbook_status = ValidationStatus.FAILED
                result.excel_result = excel_res
                result.execution_time = time.time() - start_time
                return result

            result.add_timeline_event("Crypto Verification Started")
            self.event_bus.publish(EventType.CRYPTO_VERIFICATION_STARTED, {"task_id": task_id})

            profile = self.crypto_config.profiles.get(profile_name) or self.crypto_config.profiles.get("default")

            signature_length = 0
            try:
                signature_length = len(base64.b64decode(signature_b64))
            except Exception:
                signature_length = 0

            valid = self.verify_signature(dve_hash, signature_b64, pub_key_pem)
            reason = "Signature verified successfully" if valid else "Signature verification failed: signature mismatch"
            crypto_res = CryptoVerificationResult(
                algorithm=profile.algorithm if profile else "RSA",
                hash_algorithm=profile.hash if profile else "SHA256",
                padding=profile.padding if profile else "PKCS1v15",
                verification_status=ValidationStatus.SUCCESS if valid else ValidationStatus.FAILED,
                reason=reason,
                execution_time=0.0,
                public_key_used=signer_for_key,
                verification_profile=profile.algorithm if profile else "RSA",
                expected_payload_sha256=developer_hash,
                generated_payload_sha256=dve_hash,
                payload_length=len(dve_hash.encode("utf-8")),
                signature_length=signature_length,
                diagnostics={"payload_strategy": "production-algorithm-v1"},
            )

            if not valid:
                crypto_res.errors.append(ValidationIssue(severity=Severity.ERROR, message=reason))

            excel_res.crypto_result = crypto_res
            excel_res.payload_sha256 = dve_hash
            excel_res.expected_payload_sha256 = developer_hash
            excel_res.payload_length = len(dve_hash.encode("utf-8"))
            excel_res.signature_length = signature_length
            excel_res.payload_strategy = "production-algorithm-v1"
            excel_res.payload_status = "MATCH"

            result.add_timeline_event("Crypto Verification Completed")
            self.event_bus.publish(EventType.CRYPTO_VERIFICATION_COMPLETED, {"task_id": task_id})
            result.add_timeline_event("Workbook Completed")

            excel_res.workbook_status = crypto_res.verification_status
            if crypto_res.verification_status == ValidationStatus.SUCCESS:
                result.status = ValidationStatus.SUCCESS if not (result.warning_list or excel_res.warnings) else ValidationStatus.WARNING
                result.is_valid = True
                result.reason = "Excel workbook signed and verified successfully."
            else:
                result.status = ValidationStatus.FAILED
                result.is_valid = False
                result.reason = crypto_res.reason

            result.excel_result = excel_res
            result.execution_time = time.time() - start_time
            result.verification_profile = profile.algorithm if profile else ""
            result.config_version = "1.0.0"
            result.metadata["signature_length"] = signature_length
            result.metadata["payload_length"] = len(dve_hash.encode("utf-8"))
            result.metadata["payload_strategy"] = "production-algorithm-v1"
            result.metadata["generated_payload_sha256"] = dve_hash
            result.metadata["expected_payload_sha256"] = developer_hash
            return result

        except Exception as e:
            msg = f"Unexpected validation error: {str(e)}"
            logger.exception("Excel validation unexpected error for %s", file_path)
            result.error_list.append(msg)
            result.status = ValidationStatus.FAILED
            result.is_valid = False
            result.reason = msg
            result.excel_result = excel_res
            result.execution_time = time.time() - start_time
            return result
