"""Enterprise industrial visual theme for DVE desktop GUI."""


class Theme:
	"""Centralized stylesheet tokens and component styles."""

	ORANGE_PRIMARY = "#FF7A00"
	ORANGE_DARK = "#DD6500"
	WHITE = "#FFFFFF"
	BG_SOFT = "#F2F3F5"
	TEXT_PRIMARY = "#222222"
	TEXT_SECONDARY = "#6B7280"
	BORDER = "#D7D9DD"

	MAIN_WINDOW_STYLE = """
	QWidget {
		background-color: #F4F5F7;
		color: #222222;
		font-family: "Segoe UI";
		font-size: 10pt;
	}

	QLineEdit {
		background-color: #FFFFFF;
		border: 1px solid #D7D9DD;
		border-radius: 8px;
		padding: 8px 10px;
		selection-background-color: #FF7A00;
		selection-color: #FFFFFF;
	}

	QLineEdit:focus {
		border: 1px solid #FF7A00;
	}

	QProgressBar {
		border: 1px solid #D7D9DD;
		border-radius: 7px;
		background: #FFFFFF;
		text-align: center;
		color: #222222;
		padding: 1px;
	}

	QProgressBar::chunk {
		background-color: #FF7A00;
		border-radius: 5px;
	}
	"""

	CARD_STYLE = """
	QFrame#Card {
		background-color: #FFFFFF;
		border: 1px solid #D7D9DD;
		border-radius: 10px;
		padding: 4px;
	}
	"""

	BUTTON_STYLE = """
	QPushButton {
		background-color: #FF7A00;
		color: #FFFFFF;
		border: none;
		border-radius: 8px;
		font-weight: 600;
		padding: 8px 14px;
	}
	QPushButton:hover {
		background-color: #DD6500;
	}
	QPushButton:pressed {
		background-color: #C65B00;
	}
	QPushButton:disabled {
		background-color: #C9C9C9;
		color: #777777;
	}
	"""

