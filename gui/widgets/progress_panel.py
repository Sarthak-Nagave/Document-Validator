"""Progress panel widget for runtime validation updates."""

from __future__ import annotations

from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QProgressBar, QSizePolicy


class ProgressPanel(QFrame):
	"""Displays latest activity stage and document currently being processed."""

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setObjectName("Card")
		self._completed_target = "-"
		self.setMinimumHeight(60)
		self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

		layout = QGridLayout(self)
		layout.setContentsMargins(12, 8, 12, 8)
		layout.setHorizontalSpacing(14)
		layout.setVerticalSpacing(2)

		self.stage_lbl = QLabel("Current Stage: Idle")
		self.stage_lbl.setStyleSheet("font-weight: 700;")

		self.summary_lbl = QLabel("Status: Waiting")
		self.summary_lbl.setStyleSheet("color: #374151;")

		self.completed_lbl = QLabel("Completed: -")
		self.completed_lbl.setStyleSheet("color: #374151;")

		self.progress_title_lbl = QLabel("Overall Progress")
		self.progress_title_lbl.setStyleSheet("font-weight: 600; color: #4B5563;")

		self.percent_lbl = QLabel("0%")
		self.percent_lbl.setStyleSheet("font-weight: 700; color: #374151;")

		self.progress = QProgressBar()
		self.progress.setRange(0, 100)
		self.progress.setValue(0)
		self.progress.setFormat("%p%")
		self.progress.setTextVisible(False)

		layout.addWidget(self.stage_lbl, 0, 0)
		layout.addWidget(self.summary_lbl, 1, 0)
		layout.addWidget(self.completed_lbl, 2, 0)

		layout.addWidget(self.progress_title_lbl, 0, 1)
		layout.addWidget(self.progress, 1, 1)
		layout.addWidget(self.percent_lbl, 2, 1)

		layout.setColumnStretch(0, 2)
		layout.setColumnStretch(1, 2)

	def set_completed_target(self, target: str) -> None:
		self._completed_target = target or "-"
		self.completed_lbl.setText(f"Completed: {self._completed_target}")

	def reset(self) -> None:
		"""Reset panel back to idle state for a new validation cycle."""
		self._completed_target = "-"
		self.stage_lbl.setText("Current Stage: Idle")
		self.summary_lbl.setText("Status: Waiting")
		self.completed_lbl.setText("Completed: -")
		self.percent_lbl.setText("0%")
		self.progress.setValue(0)

	def update_progress(self, payload: dict) -> None:
		"""Update progress state from worker events."""
		stage = str(payload.get("stage", "Running"))
		status = str(payload.get("status", "Processing"))
		progress = float(payload.get("progress", 0.0))
		completed_target = str(payload.get("completed_target", self._completed_target))

		self.stage_lbl.setText(f"Current Stage: {stage}")
		self.summary_lbl.setText(f"Status: {status}")
		self.completed_lbl.setText(f"Completed: {completed_target}")
		self.percent_lbl.setText(f"{progress:.0f}%")
		self.progress.setValue(int(round(progress)))

