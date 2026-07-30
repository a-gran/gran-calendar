import sys
import tomllib
from pathlib import Path

from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication

from ui.calendar_window import CalendarWindow

APPLICATION_ID = "calendar-planner"
APPLICATION_NAME = "Calendar Planner"
ICON_PATH = Path(__file__).resolve().parent / "packaging" / "calendar-planner.svg"
PROJECT_METADATA_PATH = Path(__file__).resolve().parent / "pyproject.toml"


def get_application_version():
    if not PROJECT_METADATA_PATH.exists():
        return "0.0.0"
    with PROJECT_METADATA_PATH.open("rb") as metadata_file:
        metadata = tomllib.load(metadata_file)
    return metadata["project"]["version"]


def apply_application_metadata(app):
    app.setApplicationName(APPLICATION_NAME)
    app.setApplicationVersion(get_application_version())
    app.setDesktopFileName(APPLICATION_ID)
    if ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(ICON_PATH)))


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
    apply_application_metadata(app)
    apply_dark_theme(app)
    window = CalendarWindow()
    window.setWindowTitle(f"{APPLICATION_NAME} {app.applicationVersion()}")
    if not app.windowIcon().isNull():
        window.setWindowIcon(app.windowIcon())
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
