from PySide6.QtWidgets import QFrame, QLabel, QGridLayout, QSizePolicy, QVBoxLayout

class StatCard(QFrame):
    def __init__(self, title, color, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setMinimumHeight(64)
        self.setMinimumWidth(120)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 11px; color: #6B7280; font-weight: 600;")
        
        self.value_lbl = QLabel("0")
        self.value_lbl.setStyleSheet(f"font-size: 30px; font-weight: 800; color: {color};")
        
        layout.addWidget(title_lbl)
        layout.addWidget(self.value_lbl)

    def set_value(self, val):
        self.value_lbl.setText(str(val))

class Dashboard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout = QGridLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(9)
        
        self.cards = {
            "Total": StatCard("Total Documents", "#222222"),
            "PDF": StatCard("PDF", "#FF7A00"),
            "Excel": StatCard("Excel", "#2196F3"),
            "PASS": StatCard("PASS", "#2E7D32"),
            "FAIL": StatCard("FAIL", "#C62828"),
            "WARNING": StatCard("WARNING", "#EF6C00"),
            "SKIPPED": StatCard("SKIPPED", "#616161"),
            "Execution Time": StatCard("Execution Time", "#283593"),
            "Validation Speed": StatCard("Validation Speed", "#00695C"),
            "Progress": StatCard("Progress %", "#5D4037"),
        }

        for index, card in enumerate(self.cards.values()):
            row = index // 5
            col = index % 5
            layout.addWidget(card, row, col)

        for col in range(5):
            layout.setColumnStretch(col, 1)
            
    def update_stats(self, stats_dict):
        for key, val in stats_dict.items():
            if key in self.cards:
                self.cards[key].set_value(val)
