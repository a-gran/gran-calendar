from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent


def mouse_event(event_type, point, modifiers=Qt.NoModifier):
    return QMouseEvent(event_type, point, point, Qt.LeftButton, Qt.LeftButton, modifiers)


def click_grid(grid, point, modifiers=Qt.NoModifier):
    grid.mousePressEvent(mouse_event(QMouseEvent.MouseButtonPress, point, modifiers))
    grid.mouseReleaseEvent(mouse_event(QMouseEvent.MouseButtonRelease, point, modifiers))
