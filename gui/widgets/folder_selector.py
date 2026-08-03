"""Folder selection widget used to choose validation root path."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLineEdit, QPushButton, QFileDialog, QSizePolicy


class FolderSelector(QFrame):
	"""Composite control for picking and displaying the active folder."""

	folder_selected = Signal(str)

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setObjectName("Card")
		layout = QHBoxLayout(self)
		layout.setContentsMargins(12, 10, 12, 10)
		layout.setSpacing(10)

		self.path_input = QLineEdit()
		self.path_input.setPlaceholderText("Select validation root folder...")
		self.path_input.setMinimumHeight(38)
		self.path_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
		self.path_input.textChanged.connect(self._emit_current_path)

		self.browse_btn = QPushButton("Browse")
		self.browse_btn.setMinimumHeight(36)
		self.browse_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
		self.browse_btn.clicked.connect(self._browse)
		self.browse_btn.setStyleSheet(
			"QPushButton {"
			"background-color: #FF7A00; color: #FFFFFF; border: none;"
			"border-radius: 8px; font-weight: 600; padding: 8px 14px;"
			"}"
			"QPushButton:hover { background-color: #DD6500; }"
		)

		layout.addWidget(self.path_input, 1)
		layout.addWidget(self.browse_btn)

	@property
	def selected_path(self) -> str:
		"""Return the currently selected folder path."""
		return self.path_input.text().strip()

	def _emit_current_path(self, value: str) -> None:
		"""Emit changes for both typed and browsed folder paths."""
		self.folder_selected.emit(value.strip())

	def _browse(self) -> None:
		"""Open a native folder picker and emit selected path."""
		folder = QFileDialog.getExistingDirectory(self, "Select Folder")
		if folder:
			self.path_input.setText(folder)

