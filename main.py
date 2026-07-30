import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from ui.calendar_window import CalendarWindow


def apply_dark_theme(app):
    font = QFont("Sans Serif")
    font.setStyleHint(QFont.SansSerif)
    font.setPixelSize(16)
    app.setFont(font)
    app.setStyleSheet(
        """
        QWidget {
            background-color: #0f172a;
            color: #e5e7eb;
            font-family: sans-serif;
            font-size: 16px;
        }
        QMainWindow {
            background-color: #0f172a;
        }
        QMenuBar {
            background-color: #111827;
            color: #e5e7eb;
            font-size: 16px;
            border-bottom: 1px solid #1f2937;
        }
        QMenuBar::item:selected {
            background-color: #1f2937;
        }
        QMenu {
            background-color: #111827;
            color: #e5e7eb;
            font-size: 16px;
            border: 1px solid #334155;
        }
        QMenu::item:selected {
            background-color: #2563eb;
        }
        QPushButton {
            background-color: #1f2937;
            color: #f9fafb;
            font-size: 16px;
            border: 1px solid #475569;
            border-radius: 4px;
            padding: 5px 10px;
        }
        QPushButton:hover {
            background-color: #334155;
        }
        QPushButton:pressed {
            background-color: #1d4ed8;
        }
        QPushButton:disabled {
            background-color: #111827;
            color: #64748b;
            border: 1px solid #1e293b;
        }
        QLabel {
            color: #e5e7eb;
            font-size: 16px;
        }
        QPlainTextEdit,
        QListWidget {
            background-color: #111827;
            color: #f9fafb;
            font-size: 16px;
            border: 1px solid #334155;
            selection-background-color: #2563eb;
        }
        QScrollArea {
            background-color: #0f172a;
            border: none;
        }
        QCalendarWidget {
            background-color: #0f172a;
            color: #e5e7eb;
            border: none;
        }
        QCalendarWidget QToolButton {
            background-color: #1f2937;
            color: #f9fafb;
            border: 1px solid #475569;
            border-radius: 4px;
            padding: 4px 8px;
        }
        QCalendarWidget QAbstractItemView {
            background-color: #111827;
            color: #e5e7eb;
            selection-background-color: #2563eb;
            selection-color: #ffffff;
        }
        QScrollBar:vertical {
            background-color: #111827;
            width: 12px;
        }
        QScrollBar::handle:vertical {
            background-color: #475569;
            border-radius: 4px;
        }
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0;
        }
        """
    )


def main():
    app = QApplication(sys.argv)
    apply_dark_theme(app)
    window = CalendarWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
