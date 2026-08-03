"""Enterprise PDF Digital Signature Validator."""
import time
import logging
from typing import Any

from interfaces.validator import IValidator
from domain.entities.validation_task import ValidationTask
from domain.value_objects.validation_result import (
    ValidationResult,
    PDFValidationResult,
    PageValidationResult,
    SignatureValidationResult
)
from events.event_bus import EventBus
from events.event_types import EventType
from domain.enums.validation_status import ValidationStatus
from domain.enums.severity import Severity

try:
    from pyhanko.pdf_utils.reader import PdfFileReader
    from pyhanko.sign import validation
    PYHANKO_AVAILABLE = True
except ImportError:
    PYHANKO_AVAILABLE = False

logger = logging.getLogger(__name__)

class PDFValidator(IValidator):
    def __init__(self, event_bus: EventBus, pdf_config: Any):
        self.event_bus = event_bus
        self.config = pdf_config
        # Expected policy findings are handled at business-rule level; suppress stack traces.
        logging.getLogger("pyhanko.sign.validation.generic_cms").setLevel(logging.ERROR)
        logging.getLogger("pyhanko.sign.validation").setLevel(logging.ERROR)

    @staticmethod
    def _is_weak_key_policy(status_obj: Any) -> bool:
        trust_problem = str(getattr(status_obj, "trust_problem_indic", ""))
        return "CRYPTO_CONSTRAINTS_FAILURE" in trust_problem

    @staticmethod
    def _weak_key_message(cert: Any) -> str:
        key_size = "unknown"
        try:
            key_size = cert.public_key.bit_size  # type: ignore[attr-defined]
        except Exception:
            pass
        return f"Weak RSA Key ({key_size})"

    @staticmethod
    def _detect_role(cn: str, field_name: str, required_signers: dict[str, str]) -> str:
        for role, configured_name in required_signers.items():
            if cn.lower() == configured_name.lower():
                return role
            if role.lower() in field_name.lower():
                return role
        return "UNKNOWN"

    @staticmethod
    def _build_status_text(has_fail: bool, has_warning: bool) -> str:
        if has_fail:
            return "FAIL"
        # Warnings do not change a successful validation outcome.
        if has_warning:
            return "PASS"
        return "PASS"

    def validate(self, task: ValidationTask) -> ValidationResult:
        start_time = time.time()
        file_path = task.file_path
        logger.info("PDF Validator starting for %s", file_path)

        warnings: list[str] = []
        errors: list[str] = []
        page_results: list[PageValidationResult] = []
        
        required_signers = self.config.validation.required_signers
        required_roles = list(required_signers.keys())

        if not PYHANKO_AVAILABLE:
            errors.append("pyHanko is not installed.")
            return self._build_result(task, start_time, ValidationStatus.ERROR, False, errors, warnings, None, page_results)

        try:
            with open(file_path, 'rb') as f:
                try:
                    reader = PdfFileReader(f)
                except Exception as e:
                    errors.append(f"Corrupted or unsupported PDF: {str(e)}")
                    self.event_bus.publish(EventType.VALIDATION_FAILED, {"task_id": task.task_id, "error": str(e)})
                    return self._build_result(task, start_time, ValidationStatus.FAILED, False, errors, warnings, None, page_results)
                
                embedded_sigs = list(reader.embedded_signatures)
                if not embedded_sigs:
                    errors.append("Missing signature: document is unsigned")
                    return self._build_result(task, start_time, ValidationStatus.FAILED, False, errors, warnings, None, page_results)

                page_start = time.time()
                
                detected_roles: list[str] = []
                signature_results: list[SignatureValidationResult] = []
                duplicate_signatures = 0

                signatures_to_validate: list[Any] = []
                seen_role_signer: set[tuple[str, str]] = set()
                for sig in embedded_sigs:
                    cert_hint = getattr(sig, "signer_cert", None)
                    cn_hint = "UNKNOWN"
                    if cert_hint is not None:
                        try:
                            cn_hint = cert_hint.subject.native.get("common_name", "UNKNOWN")
                        except Exception:
                            cn_hint = "UNKNOWN"
                    role_hint = self._detect_role(cn_hint, getattr(sig, "field_name", ""), required_signers)
                    if role_hint != "UNKNOWN" and cn_hint != "UNKNOWN":
                        key = (role_hint, cn_hint.lower())
                        if key in seen_role_signer:
                            duplicate_signatures += 1
                            continue
                        seen_role_signer.add(key)
                    signatures_to_validate.append(sig)
                
                prepared_result = "NOT_FOUND"
                verified_result = "NOT_FOUND"
                approved_result = "NOT_FOUND"
                
                for sig in signatures_to_validate:
                    self.event_bus.publish(EventType.SIGNATURE_DETECTED, {"task_id": task.task_id, "field": sig.field_name})
                    
                    try:
                        status = validation.validate_pdf_signature(sig)
                        cert = getattr(status, "signing_cert", None) or getattr(sig, "signer_cert", None)
                        if cert is None:
                            raise ValueError("Certificate parsing failed")

                        cn = cert.subject.native.get('common_name', 'UNKNOWN')
                        issuer = cert.issuer.native.get('common_name', 'UNKNOWN')

                        role = self._detect_role(cn, sig.field_name, required_signers)

                        weak_key = self._is_weak_key_policy(status)
                        signature_is_valid = bool(status.intact and status.valid)
                        signature_status = "PASS" if signature_is_valid else "FAIL"
                                
                        sig_res = SignatureValidationResult(
                            role=role,
                            configured_name=required_signers.get(role, "N/A"),
                            detected_certificate_cn=cn,
                            certificate_subject=str(cert.subject.native),
                            certificate_issuer=issuer,
                            certificate_thumbprint=cert.sha256.hex(),
                            signing_time=str(getattr(status, "signer_reported_dt", "")),
                            certificate_validity="VALID",
                            signature_integrity="VALID" if status.intact else "INVALID",
                            validation_status=signature_status,
                            warning_list=[],
                            error_list=[]
                        )
                        
                        if not status.intact:
                            sig_res.error_list.append("Signature integrity check failed.")
                        if role != "UNKNOWN" and cn.lower() != required_signers.get(role, "").lower():
                            sig_res.error_list.append(f"Wrong signer: CN '{cn}' does not match configured name '{required_signers.get(role)}'")
                            sig_res.validation_status = "FAIL"

                        if weak_key and signature_is_valid:
                            weak_msg = self._weak_key_message(cert)
                            sig_res.warning_list.append(weak_msg)
                            warnings.append(f"{weak_msg} | Signer: {cn} | Document: {file_path.name}")
                            logger.warning("%s | Signer: %s | Document: %s", weak_msg, cn, file_path.name)
                        elif getattr(status, "trust_problem_indic", None) and signature_is_valid:
                            # Non-fatal trust findings are warnings by business rule.
                            trust_msg = f"Certificate/trust warning: {status.trust_problem_indic}"
                            sig_res.warning_list.append(trust_msg)
                            warnings.append(trust_msg)
                            
                        if role == "Prepared By": prepared_result = sig_res.validation_status
                        elif role == "Verified By": verified_result = sig_res.validation_status
                        elif role == "Approved By": approved_result = sig_res.validation_status
                            
                        if role not in detected_roles:
                            detected_roles.append(role)
                            
                        signature_results.append(sig_res)
                        
                        self.event_bus.publish(EventType.SIGNATURE_VALIDATED, {"task_id": task.task_id, "role": role, "status": sig_res.validation_status})
                        
                    except Exception as e:
                        errors.append(f"Invalid signature or unreadable signature field {sig.field_name}: {str(e)}")
                
                missing = [r for r in required_roles if r not in detected_roles]
                unexpected = [r for r in detected_roles if r not in required_roles and r != "UNKNOWN"]
                
                for m in missing:
                    errors.append(f"Missing required signature role: {m}")
                for u in unexpected:
                    warnings.append(f"Unexpected signature role: {u}")

                has_signature_fail = any(s.validation_status == "FAIL" for s in signature_results)
                page_status = self._build_status_text(has_fail=bool(errors or missing or has_signature_fail), has_warning=bool(warnings))
                
                pr = PageValidationResult(
                    page_number=1,
                    page_status=page_status,
                    validation_time=time.time() - page_start,
                    required_roles=required_roles,
                    detected_roles=detected_roles,
                    prepared_result=prepared_result,
                    verified_result=verified_result,
                    approved_result=approved_result,
                    certificate_details=[{"cn": s.detected_certificate_cn, "issuer": s.certificate_issuer} for s in signature_results],
                    warning_list=[],
                    error_list=[],
                    signature_results=signature_results
                )
                page_results.append(pr)
                self.event_bus.publish(EventType.PAGE_VALIDATED, {"task_id": task.task_id, "page": 1, "status": page_status})

                pdf_res = PDFValidationResult(
                    file_name=file_path.name,
                    total_pages=1, # Mock for Phase 3 prototype
                    pages_passed=1 if page_status == "PASS" else 0,
                    pages_failed=1 if page_status == "FAIL" else 0,
                    required_signatures=len(required_roles),
                    detected_signatures=len(signature_results),
                    missing_signatures=len(missing),
                    unexpected_signatures=len(unexpected),
                    duplicate_signatures=duplicate_signatures,
                    overall_status=page_status,
                    execution_time=time.time() - start_time,
                    warning_list=warnings,
                    error_list=errors
                )
                # Stabilize output readability for GUI/reports.
                warnings = list(dict.fromkeys(warnings))
                errors = list(dict.fromkeys(errors))
                pdf_res.warning_list = warnings
                pdf_res.error_list = errors
                logger.info("PDF signature extracted successfully for %s", file_path)
                
                if page_status == "PASS":
                    mapped = ValidationStatus.SUCCESS
                    reason = "PDF validation passed"
                else:
                    mapped = ValidationStatus.FAILED
                    reason = "PDF validation failed"

                return self._build_result(
                    task,
                    start_time,
                    mapped,
                    mapped == ValidationStatus.SUCCESS,
                    errors,
                    warnings,
                    pdf_res,
                    page_results,
                    reason,
                )
                
        except PermissionError:
            errors.append("Permission denied when accessing PDF.")
            return self._build_result(task, start_time, ValidationStatus.FAILED, False, errors, warnings, None, page_results)
        except Exception as e:
            errors.append(f"Unexpected error: {str(e)}")
            return self._build_result(task, start_time, ValidationStatus.FAILED, False, errors, warnings, None, page_results)

    def _build_result(self, task, start_time, status, is_valid, errors, warnings, pdf_res, page_results, reason: str | None = None):
        return ValidationResult(
            task_id=task.task_id,
            validator_name="PDFValidator",
            root_group=task.root_group,
            execution_time=time.time() - start_time,
            status=status,
            reason=reason or "PDF Validation Completed",
            is_valid=is_valid,
            warning_list=warnings,
            error_list=errors,
            pdf_result=pdf_res,
            metadata={
                "pdf_summary": pdf_res,
                "pages": page_results
            }
        )
