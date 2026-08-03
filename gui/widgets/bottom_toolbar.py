"""Bottom toolbar controls for main window actions."""

from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QLabel


class BottomToolbar(QFrame):
	"""Toolbar with end-user actions at the bottom of the main UI."""

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setObjectName("Card")
		self._report_paths = {}
		layout = QHBoxLayout(self)
		layout.setContentsMargins(12, 8, 12, 8)
		layout.setSpacing(10)

		self.summary_lbl = QLabel("Ready")
		self.summary_lbl.setStyleSheet("color: #6B7280;")

		layout.addWidget(self.summary_lbl)
		layout.addStretch(1)

		self.btn_open_html = QPushButton("Open HTML")
		self.btn_open_excel = QPushButton("Open Excel")
		self.btn_open_json = QPushButton("Open JSON")

		for btn in (self.btn_open_html, self.btn_open_excel, self.btn_open_json):
			btn.setEnabled(False)
			btn.setStyleSheet(
				"QPushButton {"
				"background-color: #374151; color: #FFFFFF; border: none;"
				"border-radius: 8px; font-weight: 600; padding: 8px 12px;"
				"}"
				"QPushButton:disabled { background-color: #9CA3AF; color: #E5E7EB; }"
			)

		self.btn_open_html.clicked.connect(lambda: self._open_report("html"))
		self.btn_open_excel.clicked.connect(lambda: self._open_report("xlsx"))
		self.btn_open_json.clicked.connect(lambda: self._open_report("json"))

		layout.addWidget(self.btn_open_html)
		layout.addWidget(self.btn_open_excel)
		layout.addWidget(self.btn_open_json)

		self.btn_exit = QPushButton("Exit")
		self.btn_exit.setStyleSheet(
			"QPushButton {"
			"background-color: #FF7A00; color: #FFFFFF; border: none;"
			"border-radius: 8px; font-weight: 600; padding: 8px 16px;"
			"}"
			"QPushButton:hover { background-color: #DD6500; }"
		)
		layout.addWidget(self.btn_exit)

	def set_summary(self, text: str):
		self.summary_lbl.setText(text)

	def set_report_paths(self, report_paths: dict):
		self._report_paths = report_paths or {}
		html_ok = Path(self._report_paths.get("html", "")).exists()
		xlsx_ok = Path(self._report_paths.get("xlsx", "")).exists()
		json_ok = Path(self._report_paths.get("json", "")).exists()
		self.btn_open_html.setEnabled(html_ok)
		self.btn_open_excel.setEnabled(xlsx_ok)
		self.btn_open_json.setEnabled(json_ok)

	def _open_report(self, key: str):
		path = self._report_paths.get(key, "")
		if path and Path(path).exists():
			QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(path).resolve())))

