THEME_COLORS = {
    "dark": {
        "window_background": "#0b1120",
        "panel_background": "#0f172a",
        "field_background": "#111827",
        "text": "#e5e7eb",
        "muted_text": "#94a3b8",
        "message_text": "#93c5fd",
        "grid_line": "#334155",
        "grid_half_line": "#1e293b",
        "selection_border": "#93c5fd",
        "event_border": "#60a5fa",
        "selected_event_border": "#ffffff",
        "normal_event_background": "#0f172a",
        "normal_event_text": "#ffffff",
        "button_background": "#1f2937",
        "button_border": "#475569",
        "button_checked": "#2563eb",
        "disabled_background": "#111827",
        "disabled_text": "#64748b",
    },
    "light": {
        "window_background": "#f8fafc",
        "panel_background": "#ffffff",
        "field_background": "#f8fafc",
        "text": "#0f172a",
        "muted_text": "#475569",
        "message_text": "#2563eb",
        "grid_line": "#cbd5e1",
        "grid_half_line": "#e2e8f0",
        "selection_border": "#2563eb",
        "event_border": "#2563eb",
        "selected_event_border": "#0f172a",
        "normal_event_background": "#ffffff",
        "normal_event_text": "#0f172a",
        "button_background": "#e2e8f0",
        "button_border": "#94a3b8",
        "button_checked": "#2563eb",
        "disabled_background": "#e2e8f0",
        "disabled_text": "#94a3b8",
    },
}


def theme_colors(theme_name):
    return THEME_COLORS.get(theme_name, THEME_COLORS["dark"])


def application_style(theme_name):
    colors = theme_colors(theme_name)
    return f"QMainWindow {{ background: {colors['window_background']}; }}"


def details_panel_style(theme_name):
    colors = theme_colors(theme_name)
    return (
        f"QFrame {{ background: {colors['panel_background']}; border: none; }} "
        f"QLabel {{ color: {colors['text']}; font-family: sans-serif; font-size: 16px; }} "
        f"QPlainTextEdit {{ background: {colors['field_background']}; color: {colors['text']}; "
        f"border: 1px solid {colors['grid_line']}; font-family: sans-serif; font-size: 16px; }}"
    )


def details_label_style(theme_name):
    colors = theme_colors(theme_name)
    return f"color: {colors['muted_text']}; font-family: sans-serif; font-size: 16px;"


def details_message_style(theme_name):
    colors = theme_colors(theme_name)
    return f"color: {colors['message_text']}; font-family: sans-serif; font-size: 14px;"


DETAILS_PANEL_STYLE = details_panel_style("dark")
DETAILS_LABEL_STYLE = details_label_style("dark")
DETAILS_MESSAGE_STYLE = details_message_style("dark")


def details_time_style(pixel_size, theme_name="dark"):
    colors = theme_colors(theme_name)
    return f"color: {colors['text']}; font-family: sans-serif; font-size: {pixel_size}px; font-weight: bold;"


OVERVIEW_EVENT_ROW_STYLE = (
    "QWidget { background: transparent; border: none; }"
    "QLabel { color: #e5e7eb; border: none; font-size: 16px; }"
    "QLineEdit { background: #111827; color: #e5e7eb; border: 1px solid #475569; "
    "border-radius: 4px; font-size: 16px; padding: 2px 6px; }"
    "QPushButton { background: #1f2937; color: #fca5a5; border: 1px solid #334155; "
    "border-radius: 4px; font-size: 15px; font-weight: bold; padding: 0; }"
    "QPushButton:hover { background: #7f1d1d; color: #ffffff; border-color: #ef4444; }"
)
MONTH_BUTTON_STYLE = (
    "QPushButton { background: #1f2937; color: #e5e7eb; border: 1px solid #475569; "
    "border-radius: 4px; padding: 7px 14px; font-size: 16px; }"
    "QPushButton:checked { background: #2563eb; color: #ffffff; border: 2px solid #ffffff; "
    "font-weight: bold; padding: 6px 13px; }"
)
YEAR_SELECTOR_STYLE = (
    "QWidget { background: #1f2937; border: 1px solid #475569; border-radius: 4px; }"
    "QLabel { color: #e5e7eb; border: none; padding-left: 10px; font-size: 16px; }"
    "QPushButton { background: #263244; color: #e5e7eb; border: none; border-left: 1px solid #475569; "
    "font-size: 12px; font-weight: bold; padding: 0; }"
    "QPushButton:hover { background: #334155; }"
)
MONTH_CALENDAR_BUTTON_TEXT = "Month"
WEEK_CALENDAR_BUTTON_TEXT = "Week"
MONTH_OVERVIEW_CALENDAR_HEIGHT = 430
