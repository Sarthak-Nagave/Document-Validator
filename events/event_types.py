"""Event type definitions."""
from enum import Enum

class EventType(Enum):
    APPLICATION_STARTED = "ApplicationStarted"
    APPLICATION_SHUTDOWN = "ApplicationShutdown"
    APPLICATION_COMPLETED = "ApplicationCompleted"
    
    SCAN_STARTED = "ScanStarted"
    FOLDER_DISCOVERED = "FolderDiscovered"
    FOLDER_SKIPPED = "FolderSkipped"
    FILE_DISCOVERED = "FileDiscovered"
    
    VALIDATION_STARTED = "ValidationStarted"
    VALIDATION_COMPLETED = "ValidationCompleted"
    VALIDATION_FAILED = "ValidationFailed"
    VALIDATION_SKIPPED = "ValidationSkipped"
    
    SUMMARY_GENERATED = "SummaryGenerated"
    
    CERTIFICATE_LOADED = "CertificateLoaded"
    SIGNATURE_DETECTED = "SignatureDetected"
    SIGNATURE_VALIDATED = "SignatureValidated"
    PAGE_VALIDATED = "PageValidated"
    
    WORKBOOK_PARSED = "WorkbookParsed"
    PUBLIC_KEY_LOADED = "PublicKeyLoaded"
    PAYLOAD_BUILD_STARTED = "PayloadBuildStarted"
    PAYLOAD_BUILD_COMPLETED = "PayloadBuildCompleted"
    CRYPTO_VERIFICATION_STARTED = "CryptoVerificationStarted"
    CRYPTO_VERIFICATION_COMPLETED = "CryptoVerificationCompleted"
