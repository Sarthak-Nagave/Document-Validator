from collections import defaultdict

from PySide6.QtWidgets import QFrame, QLabel, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QStyle
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap

class ProjectTree(QFrame):
    node_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 10)
        layout.setSpacing(8)

        self._status_icons = {
            "RUNNING": self._build_status_icon("#1565C0"),
            "PASS": self._build_status_icon("#2E7D32"),
            "WARNING": self._build_status_icon("#EF6C00"),
            "FAIL": self._build_status_icon("#C62828"),
        }
        
        lbl = QLabel("Project Tree")
        lbl.setFont(QFont("Segoe UI", 14, QFont.DemiBold))
        layout.addWidget(lbl)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(False)
        self.tree.setColumnCount(1)
        self.tree.setHeaderLabels(["Project Folders"])
        self.tree.setFont(QFont("Segoe UI", 11))
        self.tree.setIconSize(QPixmap(14, 14).size())
        self.tree.setIndentation(26)
        self.tree.setUniformRowHeights(False)
        self.tree.setTextElideMode(Qt.ElideNone)
        self.tree.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tree.setWordWrap(True)
        self.tree.header().setStretchLastSection(True)
        self.tree.header().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tree.header().setStyleSheet("QHeaderView::section { padding: 7px 8px; font-weight: 600; color: #374151; }")
        self.tree.setStyleSheet(
            "QTreeWidget::item { padding: 10px 8px; min-height: 52px; color: #111111; }"
            "QTreeWidget::item:selected { background: #E3ECFA; color: #111111; }"
            "QTreeWidget::item:hover { background: #F4F7FC; }"
        )
        self.tree.setAlternatingRowColors(True)
        self.tree.setRootIsDecorated(True)
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
        root_font = self.root_node.font(0)
        root_font.setBold(True)
        root_font.setPointSize(11)
        self.root_node.setFont(0, root_font)
        self.root_node.setForeground(0, QColor("#111111"))
        self.ds_nodes = {}
        
    def add_validation_result(self, result):
        if not result.root_group:
            return
            
        group_name = result.root_group
        if group_name not in self.ds_nodes:
            node = QTreeWidgetItem([group_name])
            node.setIcon(0, self._status_icons["RUNNING"])
            node.setData(0, Qt.UserRole, group_name)
            self.root_node.addChild(node)
            self.ds_nodes[group_name] = {
                "node": node,
                "status": "RUNNING",
                "counts": defaultdict(int),
            }
            self.root_node.setExpanded(True)
            node.setExpanded(True)
            self._render_node(group_name)
            
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
            icon_key = "FAIL"
        elif total_count > 0 and pass_count == total_count:
            ds_data["status"] = "PASS"
            icon_key = "PASS"
        elif pass_count > 0 and warning_count > 0 and (pass_count + warning_count == total_count):
            ds_data["status"] = "PASS"
            icon_key = "PASS"
        elif total_count > 0 and warning_count == total_count:
            ds_data["status"] = "WARNING"
            icon_key = "WARNING"
        else:
            ds_data["status"] = "RUNNING"
            icon_key = "RUNNING"

        ds_data["icon_key"] = icon_key
        self._render_node(group_name)

        root_font = self.root_node.font(0)
        root_font.setBold(True)
        self.root_node.setFont(0, root_font)

    def _build_status_icon(self, color_hex: str) -> QIcon:
        pixmap = QPixmap(14, 14)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(color_hex))
        painter.drawEllipse(1, 1, 12, 12)
        painter.end()
        return QIcon(pixmap)

    def _render_node(self, group_name: str):
        ds_data = self.ds_nodes[group_name]
        counts = ds_data["counts"]
        pass_count = counts.get("PASS", 0)
        fail_count = counts.get("FAIL", 0)
        warning_count = counts.get("WARNING", 0)

        display_text = (
            f"{group_name}\n"
            f"PASS {pass_count}   FAIL {fail_count}   WARNING {warning_count}"
        )
        node = ds_data["node"]
        node.setText(0, display_text)
        node.setIcon(0, self._status_icons.get(ds_data.get("icon_key", "RUNNING"), self._status_icons["RUNNING"]))
        node.setForeground(0, QColor("#111111"))

        name_font = QFont(self.tree.font())
        name_font.setBold(False)
        name_font.setPointSize(11)
        node.setFont(0, name_font)

        self._update_node_tooltip(node, group_name)

    def _update_node_tooltip(self, node: QTreeWidgetItem, folder_name: str):
        available_width = self.tree.viewport().width() - 70 - (self._node_depth(node) * self.tree.indentation())
        text_width = self.tree.fontMetrics().horizontalAdvance(folder_name)
        if text_width > max(available_width, 80):
            node.setToolTip(0, folder_name)
        else:
            node.setToolTip(0, "")

    def _node_depth(self, node: QTreeWidgetItem) -> int:
        depth = 0
        parent = node.parent()
        while parent is not None:
            depth += 1
            parent = parent.parent()
        return depth

    def resizeEvent(self, event):
        super().resizeEvent(event)
        for data in self.ds_nodes.values():
            node = data.get("node")
            if node is None:
                continue
            folder_name = node.data(0, Qt.UserRole) or ""
            self._update_node_tooltip(node, folder_name)

    def _on_selection_changed(self):
        selected = self.tree.selectedItems()
        if selected:
            group_name = selected[0].data(0, Qt.UserRole)
            if group_name in self.ds_nodes:
                self.node_selected.emit(group_name)
            else:
                self.node_selected.emit("")
