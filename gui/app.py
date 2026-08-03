"""GUI application bootstrap for the DVE desktop interface."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Optional

from PySide6.QtWidgets import QApplication

from app.dependency_container import DependencyContainer
from gui.main_window import MainWindow


def run_gui(root_path: Path, container: Optional[DependencyContainer] = None) -> int:
	"""Create and run the Qt application with the main window."""
	app = QApplication.instance() or QApplication(sys.argv)
	container = container or DependencyContainer(root_path)
	window = MainWindow(container.engine, container)
	window.show()
	return app.exec()

