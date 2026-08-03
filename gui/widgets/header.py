"""Application header widget for DVE desktop UI."""

from pathlib import Path

from PySide6.QtCore import QUrl, Signal
from PySide6.QtGui import QDesktopServices, QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget


class Header(QFrame):
	"""Header area showing product title and version."""

	exit_requested = Signal()

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setObjectName("Card")
		self._report_paths = {}

		layout = QHBoxLayout(self)
		layout.setContentsMargins(16, 10, 16, 10)
		layout.setSpacing(12)

		accent = QFrame()
		accent.setMinimumWidth(6)
		accent.setMaximumWidth(6)
		accent.setStyleSheet("background-color: #FF7A00; border-radius: 3px;")

		text_block = QWidget()
		text_layout = QVBoxLayout(text_block)
		text_layout.setContentsMargins(0, 0, 0, 0)
		text_layout.setSpacing(2)

		title = QLabel("Document Validation Engine")
		title.setFont(QFont("Segoe UI", 18, QFont.Bold))

		subtitle = QLabel("Enterprise Validation Platform")
		subtitle.setStyleSheet("color: #6B7280; font-size: 10pt;")

		text_layout.addWidget(title)
		text_layout.addWidget(subtitle)

		self.btn_open_html = QPushButton("Open HTML")
		self.btn_open_excel = QPushButton("Open Excel")
		self.btn_open_json = QPushButton("Open JSON")
		for btn in (self.btn_open_html, self.btn_open_excel, self.btn_open_json):
			btn.setEnabled(False)
			btn.setMinimumHeight(36)
			btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
			btn.setStyleSheet(
				"QPushButton {"
				"background-color: #374151; color: #FFFFFF; border: none;"
				"border-radius: 8px; font-weight: 600; padding: 8px 12px;"
				"}"
				"QPushButton:hover { background-color: #FF7A00; }"
				"QPushButton:disabled { background-color: #9CA3AF; color: #E5E7EB; }"
			)

		self.btn_open_html.clicked.connect(lambda: self._open_report("html"))
		self.btn_open_excel.clicked.connect(lambda: self._open_report("xlsx"))
		self.btn_open_json.clicked.connect(lambda: self._open_report("json"))

		version = QLabel("DVE v1.0")
		version.setStyleSheet(
			"color: #FF7A00; font-weight: 700; "
			"padding: 4px 10px; border: 1px solid #FFD1AD; border-radius: 10px;"
		)

		self.btn_exit = QPushButton("Exit")
		self.btn_exit.setMinimumHeight(36)
		self.btn_exit.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
		self.btn_exit.setStyleSheet(
			"QPushButton {"
			"background-color: #FF7A00; color: #FFFFFF; border: none;"
			"border-radius: 8px; font-weight: 600; padding: 8px 16px;"
			"}"
			"QPushButton:hover { background-color: #DD6500; }"
		)
		self.btn_exit.clicked.connect(self.exit_requested.emit)

		layout.addWidget(accent)
		layout.addWidget(text_block)
		layout.addStretch(1)
		layout.addWidget(self.btn_open_html)
		layout.addWidget(self.btn_open_excel)
		layout.addWidget(self.btn_open_json)
		layout.addWidget(version)
		layout.addWidget(self.btn_exit)

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

