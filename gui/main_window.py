import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QSplitter, QLabel, QSizePolicy
)
from PySide6.QtCore import QSettings, Qt
from gui.theme import Theme
from gui.widgets.header import Header
from gui.widgets.folder_selector import FolderSelector
from gui.widgets.dashboard import Dashboard
from gui.widgets.progress_panel import ProgressPanel
from gui.widgets.results_table import ResultsTable
from gui.widgets.project_tree import ProjectTree
from gui.widgets.detail_panel import DetailPanel
from gui.worker import ValidationWorker

class MainWindow(QMainWindow):
    def __init__(self, engine, container):
        super().__init__()
        self.engine = engine
        self.container = container
        self.worker = None
        self.target_folder = ""
        self.validation_results = []
        self.settings = QSettings("DVE", "DocumentValidator")
        
        self.setWindowTitle("Document Validation Engine (DVE) - v1.0")
        self.setMinimumSize(1200, 780)
        self.setStyleSheet(Theme.MAIN_WINDOW_STYLE)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(12)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        self._init_ui()
        self._connect_signals()
        
    def _init_ui(self):
        # Header
        self.header = Header()
        self.main_layout.addWidget(self.header)

        self.folder_section_label = QLabel("Folder Selection")
        self.folder_section_label.setStyleSheet("font-weight: 600; color: #4B5563;")
        self.main_layout.addWidget(self.folder_section_label)
        
        # Folder Selection + Validation Controls (single row)
        top_layout = QHBoxLayout()
        top_layout.setSpacing(12)
        self.folder_selector = FolderSelector()
        self.folder_selector.setStyleSheet(Theme.CARD_STYLE)
        self.folder_selector.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.start_btn = QPushButton("START VALIDATION")
        self.start_btn.setStyleSheet(Theme.BUTTON_STYLE)
        self.start_btn.setMinimumHeight(36)
        self.start_btn.setMinimumWidth(170)
        self.start_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.start_btn.setEnabled(False)

        self.cancel_btn = QPushButton("CANCEL")
        self.cancel_btn.setStyleSheet(Theme.BUTTON_STYLE)
        self.cancel_btn.setMinimumHeight(36)
        self.cancel_btn.setMinimumWidth(130)
        self.cancel_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.cancel_btn.setEnabled(False)
        
        top_layout.addWidget(self.folder_selector, 1)
        top_layout.addWidget(self.start_btn)
        top_layout.addWidget(self.cancel_btn)
        self.main_layout.addLayout(top_layout)
        
        # Dashboard
        self.dashboard = Dashboard()
        self.dashboard.setStyleSheet(Theme.CARD_STYLE)
        self.main_layout.addWidget(self.dashboard)
        
        # Splitter for the 3 panels
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(8)
        self.main_layout.addWidget(self.splitter, stretch=1)
        
        # 1. Left Panel (Project Tree)
        self.project_tree = ProjectTree()
        self.project_tree.setMinimumWidth(260)
        self.project_tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.splitter.addWidget(self.project_tree)
        
        # 2. Center Panel (Results Table)
        self.results_table = ResultsTable()
        self.results_table.setMinimumWidth(360)
        self.results_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.splitter.addWidget(self.results_table)
        
        # 3. Right Panel (Detail Panel)
        self.detail_panel = DetailPanel()
        self.detail_panel.setMinimumWidth(280)
        self.detail_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.splitter.addWidget(self.detail_panel)
        
        # Target ratio: Tree ~25%, Table ~55%, Details ~20%
        self.splitter.setSizes([300, 660, 240])
        self.splitter.setStretchFactor(0, 25)
        self.splitter.setStretchFactor(1, 55)
        self.splitter.setStretchFactor(2, 20)
        
        # Progress
        self.progress_panel = ProgressPanel()
        self.progress_panel.setStyleSheet(Theme.CARD_STYLE)
        self.progress_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.main_layout.addWidget(self.progress_panel)

        self._restore_splitter_state()
        
    def _connect_signals(self):
        self.folder_selector.folder_selected.connect(self._on_folder_selected)
        self.start_btn.clicked.connect(self._start_validation)
        self.cancel_btn.clicked.connect(self._cancel_validation)
        self.header.exit_requested.connect(self.close)
        self.project_tree.node_selected.connect(self._filter_table_by_ds)
        self.results_table.row_clicked.connect(self._show_details)
        
    def _on_folder_selected(self, path):
        self.start_btn.setEnabled(bool(path and os.path.isdir(path)))
        self.target_folder = path
        
    def _start_validation(self):
        if not self.target_folder:
            return

        self.validation_results = []
        self.results_table.clear_results()
        self.project_tree.reset_tree(self.target_folder)
        self.detail_panel.reset()
        self.progress_panel.reset()
        self.dashboard.update_stats(
            {
                "Total": 0,
                "PDF": 0,
                "Excel": 0,
                "PASS": 0,
                "FAIL": 0,
                "WARNING": 0,
                "SKIPPED": 0,
                "Execution Time": "0.00s",
                "Validation Speed": "0.00/s",
                "Progress": "0%",
            }
        )
        self.header.set_report_paths({})
        selected = os.path.basename(self.target_folder.rstrip("/\\")) if self.target_folder else "-"
        self.progress_panel.set_completed_target(selected)
        
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.folder_selector.setEnabled(False)
        
        self.worker = ValidationWorker(self.engine, self.container, self.target_folder)
        self.worker.progress_updated.connect(self.progress_panel.update_progress)
        self.worker.dashboard_updated.connect(self.dashboard.update_stats)
        self.worker.result_added.connect(self.results_table.add_result)
        self.worker.result_added.connect(self.project_tree.add_validation_result)
        self.worker.result_added.connect(self._cache_result)
        self.worker.validation_completed.connect(self._on_validation_completed)
        self.worker.validation_finished.connect(self._on_validation_finished)
        self.worker.error_occurred.connect(self._on_error)

        self.worker.start()

    def _cache_result(self, raw_result):
        self.validation_results.append(raw_result)

    def _cancel_validation(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.cancel_btn.setEnabled(False)
            self.progress_panel.update_progress(
                {
                    "stage": "Cancelling",
                    "status": "Cancellation Requested",
                    "progress": float(self.progress_panel.progress.value()),
                    "completed_target": os.path.basename(self.target_folder.rstrip("/\\")) if self.target_folder else "-",
                }
            )

    def _on_validation_completed(self, payload: dict):
        stats = payload.get("stats", {}) if isinstance(payload, dict) else {}
        report_paths = payload.get("report_paths", {}) if isinstance(payload, dict) else {}
        root_name = payload.get("root_name", "") if isinstance(payload, dict) else ""

        if stats:
            self.dashboard.update_stats(stats)
        self.header.set_report_paths(report_paths)

        if self.results_table.table.rowCount() > 0:
            self.results_table.table.selectRow(0)

        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.folder_selector.setEnabled(True)
        self.progress_panel.set_completed_target(root_name or "Validation")
        self.progress_panel.update_progress(
            {
                "stage": "Completed",
                "status": "Validation Completed Successfully",
                "progress": 100.0,
                "completed_target": root_name or "Validation",
            }
        )
        
    def _on_validation_finished(self):
        if self.worker is not None:
            self.worker.deleteLater()
            self.worker = None
        self.cancel_btn.setEnabled(False)
        
    def _on_error(self, err_msg):
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.folder_selector.setEnabled(True)
        self.progress_panel.update_progress(
            {
                "stage": "Failed",
                "status": "Validation Failed",
                "progress": float(self.progress_panel.progress.value()),
                "completed_target": os.path.basename(self.target_folder.rstrip("/\\")) if self.target_folder else "-",
            }
        )
        QMessageBox.critical(self, "Error", f"A critical error occurred:\n{err_msg}")
        
    def _filter_table_by_ds(self, group_name):
        self.results_table.filter_by_folder(group_name)
                
    def _show_details(self, res_dict, raw_result):
        self.detail_panel.show_result(res_dict, raw_result)

    def _restore_splitter_state(self):
        raw_state = self.settings.value("main/splitter_state")
        if raw_state:
            self.splitter.restoreState(raw_state)
        else:
            self.splitter.setSizes([300, 660, 240])

    def _save_splitter_state(self):
        self.settings.setValue("main/splitter_state", self.splitter.saveState())

    def closeEvent(self, event):
        self._save_splitter_state()
        super().closeEvent(event)
