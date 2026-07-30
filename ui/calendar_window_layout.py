from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget


def setup_calendar_window_layout(window):
    central_widget = QWidget()
    layout = QVBoxLayout()
    window.setup_event_details_panel()
    window.setup_week_navigation(layout)
    window.setup_calendar_views()
    content_layout = QHBoxLayout()
    content_layout.addWidget(window.calendar_view_stack, 1)
    content_layout.addWidget(window.event_details_panel)
    layout.addLayout(content_layout)
    central_widget.setLayout(layout)
    window.setCentralWidget(central_widget)
