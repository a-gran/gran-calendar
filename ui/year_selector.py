from datetime import date

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.calendar_styles import YEAR_SELECTOR_STYLE


class YearSelector(QWidget):
    valueChanged = Signal(int)

    def __init__(self):
        super().__init__()
        self.minimum_year = 1900
        self.maximum_year = 3000
        self.current_year = date.today().year
        self.year_label = QLabel()
        self.up_button = QPushButton("▲")
        self.down_button = QPushButton("▼")
        self.up_button.setFixedSize(30, 16)
        self.down_button.setFixedSize(30, 16)
        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)
        button_layout.addWidget(self.up_button)
        button_layout.addWidget(self.down_button)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.year_label, 1)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.setFixedHeight(34)
        self.setFixedWidth(124)
        self.setStyleSheet(YEAR_SELECTOR_STYLE)
        self.up_button.clicked.connect(lambda: self.setValue(self.current_year + 1))
        self.down_button.clicked.connect(lambda: self.setValue(self.current_year - 1))
        self.update_label()

    def setRange(self, minimum_year, maximum_year):
        self.minimum_year = minimum_year
        self.maximum_year = maximum_year
        self.setValue(self.current_year)

    def setValue(self, year):
        bounded_year = min(max(year, self.minimum_year), self.maximum_year)
        if bounded_year == self.current_year:
            self.update_label()
            return
        self.current_year = bounded_year
        self.update_label()
        self.valueChanged.emit(self.current_year)

    def value(self):
        return self.current_year

    def update_label(self):
        self.year_label.setText(str(self.current_year))
