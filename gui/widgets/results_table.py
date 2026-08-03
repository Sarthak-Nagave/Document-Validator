from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHeaderView, QTableWidget, QTableWidgetItem, QVBoxLayout
from PySide6.QtGui import QColor


STATUS_ICON = {
    "PASS": "🟢 PASS",
    "FAIL": "🔴 FAIL",
    "WARNING": "🟡 WARNING",
    "SKIPPED": "⚪ SKIPPED",
}

class ResultsTable(QFrame):
    row_clicked = Signal(object, object) # dict, raw_result
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        layout = QVBoxLayout(self)
        
        self.table = QTableWidget(0, 10)
        self.table.setHorizontalHeaderLabels([
            "Status", "Document", "Folder", "Type", "Validation", "Signer", "Execution Time", "Result", "Reason", "Warnings"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setSectionResizeMode(8, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(34)
        self.table.setStyleSheet(
            "QTableWidget { gridline-color: #E5E7EB; alternate-background-color: #F8FAFC; }"
            "QHeaderView::section { background-color: #EEF1F4; color: #1F2937; padding: 7px; border: none; border-right: 1px solid #D7D9DD; font-weight: 600; }"
            "QTableWidget::item:selected { background: #DCEBFF; color: #111827; }"
        )
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

        # Recommended enterprise widths.
        self.table.setColumnWidth(0, 70)
        self.table.setColumnWidth(1, 320)
        self.table.setColumnWidth(2, 200)
        self.table.setColumnWidth(3, 80)
        self.table.setColumnWidth(4, 180)
        self.table.setColumnWidth(5, 180)
        self.table.setColumnWidth(6, 100)
        self.table.setColumnWidth(7, 90)
        self.table.setColumnWidth(9, 180)
        
        layout.addWidget(self.table)
        
        self.data_rows = []

    @staticmethod
    def _status_to_result(status: str) -> str:
        status_upper = (status or "").upper()
        if "SUCCESS" in status_upper:
            return "PASS"
        if "WARNING" in status_upper:
            return "WARNING"
        if "SKIPPED" in status_upper:
            return "SKIPPED"
        return "FAIL"

    @staticmethod
    def _row_color(result_text: str) -> QColor | None:
        if result_text == "PASS":
            return QColor("#E8F5E9")
        if result_text == "FAIL":
            return QColor("#FFEBEE")
        if result_text == "WARNING":
            return QColor("#FFF3E0")
        if result_text == "SKIPPED":
            return QColor("#F5F5F5")
        return None

    def clear_results(self):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        self.data_rows = []
        self.table.setSortingEnabled(True)

    def filter_by_folder(self, group_name: str | None):
        if not group_name:
            for row in range(self.table.rowCount()):
                self.table.setRowHidden(row, False)
            return
        for row in range(self.table.rowCount()):
            if row < len(self.data_rows):
                _, raw_result = self.data_rows[row]
                match = getattr(raw_result, "root_group", "") == group_name
                self.table.setRowHidden(row, not match)
        
    def add_result(self, raw_result):
        if not raw_result:
            return

        file_name = raw_result.task.file_path.name if hasattr(raw_result.task, 'file_path') else "Unknown"
        doc_type = raw_result.task.extension.upper().replace('.', '') if hasattr(raw_result.task, 'extension') else ""
        folder = raw_result.root_group if hasattr(raw_result, 'root_group') else ""
        status = raw_result.status.value if hasattr(raw_result.status, 'value') else str(raw_result.status)
        validation = getattr(raw_result, "validator_name", "")
        signer = "N/A"
        if getattr(raw_result, "pdf_result", None):
            sigs = getattr(raw_result.pdf_result, "detected_signatures", 0)
            signer = f"{sigs} signature(s)"
        elif getattr(raw_result, "excel_result", None):
            signer = raw_result.excel_result.sheet1_signer or "Unknown"

        time_taken = raw_result.execution_time if hasattr(raw_result, 'execution_time') else 0
        reason = raw_result.reason if hasattr(raw_result, 'reason') else ""
        warnings = ", ".join(getattr(raw_result, "warning_list", []) or [])

        result_text = self._status_to_result(status)
        status_icon = STATUS_ICON.get(result_text, "🔴 FAIL")
            
        res_dict = {
            "status": status_icon,
            "document": file_name,
            "folder": folder,
            "type": doc_type,
            "validation": validation,
            "signer": signer,
            "execution_time": f"{time_taken:.3f}s",
            "result": result_text,
            "reason": reason,
            "warnings": warnings,
        }
        
        row = self.table.rowCount()
        self.table.setSortingEnabled(False)
        self.table.insertRow(row)
        color = self._row_color(result_text)
            
        items = [
            QTableWidgetItem(res_dict.get("status", "")),
            QTableWidgetItem(res_dict.get("document", "")),
            QTableWidgetItem(res_dict.get("folder", "")),
            QTableWidgetItem(res_dict.get("type", "")),
            QTableWidgetItem(res_dict.get("validation", "")),
            QTableWidgetItem(res_dict.get("signer", "")),
            QTableWidgetItem(res_dict.get("execution_time", "")),
            QTableWidgetItem(res_dict.get("result", "")),
            QTableWidgetItem(res_dict.get("reason", "")),
            QTableWidgetItem(res_dict.get("warnings", "")),
        ]
        
        for col, it in enumerate(items):
            it.setData(Qt.UserRole, res_dict)
            if color:
                it.setBackground(color)
            self.table.setItem(row, col, it)
            
        self.data_rows.append((res_dict, raw_result))
        self.table.setSortingEnabled(True)
        
    def _on_selection_changed(self):
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            if 0 <= row < len(self.data_rows):
                res_dict, raw_res = self.data_rows[row]
                self.row_clicked.emit(res_dict, raw_res)
