from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QScrollArea, QWidget, QFormLayout, QToolButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class CollapsibleSection(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self._expanded = True

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.toggle_btn = QToolButton()
        self.toggle_btn.setText(f"▼ {title}")
        self.toggle_btn.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.toggle_btn.setStyleSheet("QToolButton { font-weight: 700; color: #374151; text-align: left; }")
        self.toggle_btn.clicked.connect(self._toggle)

        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(8, 2, 0, 4)
        self.body_layout.setSpacing(3)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #E5E7EB;")

        layout.addWidget(self.toggle_btn)
        layout.addWidget(line)
        layout.addWidget(self.body)

    def _toggle(self):
        self._expanded = not self._expanded
        self.body.setVisible(self._expanded)
        text = self.toggle_btn.text()
        title = text[2:] if len(text) > 2 else text
        self.toggle_btn.setText(("▼ " if self._expanded else "▶ ") + title)

class DetailPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setMinimumWidth(350)
        
        main_layout = QVBoxLayout(self)
        
        self.title_lbl = QLabel("Validation Details")
        self.title_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        main_layout.addWidget(self.title_lbl)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("QScrollArea { background-color: transparent; }")
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignTop)
        self.content_layout.setSpacing(8)
        self._active_section = None
        
        self.scroll.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll)

    def reset(self):
        self.clear_details()
        self.title_lbl.setText("Validation Details")
        
    def clear_details(self):
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
    def add_section(self, title):
        section = CollapsibleSection(title)
        self.content_layout.addWidget(section)
        self._active_section = section
        
    def add_field(self, label, value, is_status=False):
        row = QWidget()
        layout = QFormLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        
        val_lbl = QLabel(str(value))
        val_lbl.setWordWrap(True)
        val_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        if is_status:
            val_lbl.setFont(QFont("Segoe UI", 9, QFont.Bold))
            if "PASS" in str(value).upper():
                val_lbl.setStyleSheet("color: #388E3C;")
            elif "FAIL" in str(value).upper():
                val_lbl.setStyleSheet("color: #D32F2F;")
            elif "WARN" in str(value).upper():
                val_lbl.setStyleSheet("color: #FF9800;")
                
        lbl_obj = QLabel(label)
        lbl_obj.setStyleSheet("color: #616161;")
        layout.addRow(lbl_obj, val_lbl)
        if self._active_section is not None:
            self._active_section.body_layout.addWidget(row)
        else:
            self.content_layout.addWidget(row)
        
    def show_result(self, result_dict, raw_result_obj):
        self.clear_details()
        if not raw_result_obj:
            return
            
        task = getattr(raw_result_obj, "task", None)
        file_name = task.file_path.name if hasattr(task, 'file_path') else "Unknown"
        folder = getattr(raw_result_obj, "root_group", "")
        file_type = getattr(task, "extension", "")
        file_size = getattr(task, "file_size", 0)
        self.title_lbl.setText(f"Details: {file_name}")
        
        status = raw_result_obj.status.value if hasattr(raw_result_obj.status, 'value') else str(raw_result_obj.status)
        
        self.add_section("General")
        self.add_field("File Name", file_name)
        self.add_field("Folder", folder)
        self.add_field("File Type", file_type)
        self.add_field("File Size", f"{file_size} bytes")

        self.add_section("Validation Summary")
        self.add_field("Status", status, is_status=True)
        self.add_field("PASS / FAIL", "PASS" if status == "SUCCESS" else "FAIL", is_status=True)
        self.add_field("Reason", getattr(raw_result_obj, "reason", ""))
        self.add_field("Execution Time", f"{getattr(raw_result_obj, 'execution_time', 0.0):.3f} s")
        self.add_field("Validation", getattr(raw_result_obj, "validator_name", ""))
            
        if raw_result_obj.error_list:
            self.add_field("Errors", ", ".join(raw_result_obj.error_list))
        if raw_result_obj.warning_list:
            self.add_field("Warnings", ", ".join(raw_result_obj.warning_list))

        self.add_section("Audit Information")
        self.add_field("Audit ID", getattr(raw_result_obj, "audit_id", ""))
        self.add_field("Execution ID", getattr(raw_result_obj, "execution_id", ""))
        self.add_field("Timestamp", getattr(raw_result_obj, "timestamp", ""))
        self.add_field("Fingerprint", getattr(raw_result_obj, "document_fingerprint", ""))
        self.add_field("Validator Version", getattr(raw_result_obj, "validator_version", ""))
        self.add_field("Config Version", getattr(raw_result_obj, "config_version", ""))
            
        if getattr(raw_result_obj, "pdf_result", None):
            self._render_pdf(raw_result_obj.pdf_result, raw_result_obj)
        elif getattr(raw_result_obj, "excel_result", None):
            self._render_excel(raw_result_obj.excel_result)

        timeline = getattr(raw_result_obj, "timeline", []) or []
        if timeline:
            self.add_section("Timeline")
            for evt in timeline:
                self.add_field("Event", f"{evt.event} @ {evt.timestamp}")

    def _render_pdf(self, pdf, raw_result_obj):
        self.add_section("PDF Details")
        self.add_field("Required Signers", pdf.required_signatures)
        self.add_field("Detected Signers", pdf.detected_signatures)
        self.add_field("Overall Status", pdf.overall_status, is_status=True)
        self.add_field("Certificate", "Available in signature-level validation output")
        self.add_field("Timestamp", getattr(raw_result_obj, "timestamp", ""))
        self.add_field("Algorithm", getattr(raw_result_obj, "verification_profile", ""))
        
        self.add_section("Pages")
        self.add_field("Total Pages", pdf.total_pages)
        self.add_field("Pages Passed", pdf.pages_passed)
        self.add_field("Pages Failed", pdf.pages_failed)

        if getattr(pdf, "warning_list", None):
            self.add_section("Warnings")
            self.add_field("PDF Warnings", ", ".join(pdf.warning_list))
        if getattr(pdf, "error_list", None):
            self.add_section("Errors")
            self.add_field("PDF Errors", ", ".join(pdf.error_list))

    def _render_excel(self, excel):
        self.add_section("Excel Details")
        self.add_field("Workbook", excel.workbook_name)
        self.add_field("Sheet1 Signer", excel.sheet1_signer)
        self.add_field("Approved By", excel.approved_by_signer)
        self.add_field("Public Key", excel.public_key)
        self.add_field("Signer Match", "PASS" if excel.signer_match else "FAIL", is_status=True)
        self.add_field("Workbook Status", excel.workbook_status.value if hasattr(excel.workbook_status, "value") else excel.workbook_status, is_status=True)
        if getattr(excel, "payload_sha256", ""):
            self.add_field("Payload SHA256", excel.payload_sha256)
        if getattr(excel, "expected_payload_sha256", ""):
            self.add_field("Expected Payload SHA256", excel.expected_payload_sha256)
        if getattr(excel, "payload_strategy", ""):
            self.add_field("Payload Strategy", excel.payload_strategy)
        if getattr(excel, "payload_status", ""):
            self.add_field("Payload Status", excel.payload_status, is_status=True)
        if getattr(excel, "payload_length", 0):
            self.add_field("Payload Length", excel.payload_length)
        if getattr(excel, "signature_length", 0):
            self.add_field("Signature Length", excel.signature_length)
        
        if excel.crypto_result:
            self.add_section("RSA Verification")
            self.add_field("Algorithm", excel.crypto_result.algorithm)
            self.add_field("Public Key", excel.crypto_result.public_key_used)
            self.add_field("Hash", excel.crypto_result.hash_algorithm)
            self.add_field("Padding", excel.crypto_result.padding)
            self.add_field("Status", excel.crypto_result.verification_status.value if hasattr(excel.crypto_result.verification_status, 'value') else excel.crypto_result.verification_status, is_status=True)
            self.add_field("Reason", excel.crypto_result.reason)

        if excel.warnings:
            self.add_section("Warnings")
            self.add_field("Excel Warnings", ", ".join(issue.message for issue in excel.warnings))
        if excel.errors:
            self.add_section("Errors")
            self.add_field("Excel Errors", ", ".join(issue.message for issue in excel.errors))
