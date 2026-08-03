from collections import defaultdict

from PySide6.QtWidgets import QFrame, QLabel, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QStyle
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor, QFont

class ProjectTree(QFrame):
    node_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        layout = QVBoxLayout(self)
        
        lbl = QLabel("Project Tree")
        lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(lbl)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(False)
        self.tree.setColumnCount(1)
        self.tree.setHeaderLabels(["Project Folders"])
        self.tree.setFont(QFont("Segoe UI", 10))
        self.tree.setTextElideMode(Qt.ElideNone)
        self.tree.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tree.setWordWrap(True)
        self.tree.setStyleSheet(
            "QTreeWidget::item { padding: 8px 6px; min-height: 34px; }"
            "QTreeWidget::item:selected { background: #E8EEF8; color: #1F2937; }"
        )
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.tree)
        
        self.root_node = QTreeWidgetItem(["DOC"])
        self.root_node.setIcon(0, self.style().standardIcon(QStyle.SP_DirOpenIcon))
        self.tree.addTopLevelItem(self.root_node)
        self.root_node.setExpanded(True)
        
        self.ds_nodes = {}

    def reset_tree(self, root_path: str):
        self.tree.clear()
        root_label = "DOC"
        if root_path:
            normalized = root_path.replace("\\", "/").rstrip("/")
            root_label = normalized.split("/")[-1] or "DOC"
        self.root_node = QTreeWidgetItem([root_label])
        self.root_node.setIcon(0, self.style().standardIcon(QStyle.SP_DirOpenIcon))
        self.root_node.setData(0, Qt.UserRole, "")
        self.tree.addTopLevelItem(self.root_node)
        self.root_node.setExpanded(True)
        self.ds_nodes = {}
        
    def add_validation_result(self, result):
        if not result.root_group:
            return
            
        group_name = result.root_group
        if group_name not in self.ds_nodes:
            node = QTreeWidgetItem([group_name])
            node.setIcon(0, self.style().standardIcon(QStyle.SP_DirIcon))
            node.setData(0, Qt.UserRole, group_name)
            self.root_node.addChild(node)
            self.ds_nodes[group_name] = {
                "node": node,
                "status": "RUNNING",
                "counts": defaultdict(int),
            }
            self.root_node.setExpanded(True)
            node.setExpanded(True)
            
        ds_data = self.ds_nodes[group_name]
        status = result.status.value.upper() if hasattr(result.status, "value") else str(result.status).upper()

        if status == "SUCCESS":
            ds_data["counts"]["PASS"] += 1
        elif status == "WARNING":
            ds_data["counts"]["WARNING"] += 1
        elif status == "SKIPPED":
            ds_data["counts"]["SKIPPED"] += 1
        else:
            ds_data["counts"]["FAIL"] += 1
        
        self._recalculate_status(group_name)
        
    def _recalculate_status(self, group_name):
        ds_data = self.ds_nodes[group_name]
        counts = ds_data["counts"]
        pass_count = counts.get("PASS", 0)
        fail_count = counts.get("FAIL", 0)
        warning_count = counts.get("WARNING", 0)
        skipped_count = counts.get("SKIPPED", 0)
        total_count = pass_count + fail_count + warning_count + skipped_count

        if fail_count > 0:
            ds_data["status"] = "FAIL"
            icon = "🔴"
            color = QColor("#C62828")
            status_text = "FAIL"
        elif total_count > 0 and pass_count == total_count:
            ds_data["status"] = "PASS"
            icon = "🟢"
            color = QColor("#2E7D32")
            status_text = "PASS"
        elif pass_count > 0 and warning_count > 0 and (pass_count + warning_count == total_count):
            ds_data["status"] = "PASS"
            icon = "🟢"
            color = QColor("#2E7D32")
            status_text = "PASS ⚠"
        elif total_count > 0 and warning_count == total_count:
            ds_data["status"] = "WARNING"
            icon = "🟡"
            color = QColor("#EF6C00")
            status_text = "WARNING"
        else:
            ds_data["status"] = "RUNNING"
            icon = "🔵"
            color = QColor("#1565C0")
            status_text = "RUNNING"

        text = (
            f"{icon} {group_name}\n"
            f"({pass_count} PASS | {fail_count} FAIL | {warning_count} WARNING)"
        )
            
        node = ds_data["node"]
        node.setText(0, text)
        node.setForeground(0, color)
        font = node.font(0)
        font.setBold(True)
        node.setFont(0, font)

        root_font = self.root_node.font(0)
        root_font.setBold(True)
        self.root_node.setFont(0, root_font)

    def _on_selection_changed(self):
        selected = self.tree.selectedItems()
        if selected:
            group_name = selected[0].data(0, Qt.UserRole)
            if group_name in self.ds_nodes:
                self.node_selected.emit(group_name)
            else:
                self.node_selected.emit("")
