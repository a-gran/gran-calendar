from PySide6.QtWidgets import QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QSpinBox, QVBoxLayout

from ui.calendar_styles import application_style, details_message_style, details_panel_style, details_time_style


class CalendarSettingsMixin:
    def open_visual_settings_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.setModal(True)

        theme_input = QComboBox()
        theme_input.addItem("Dark", "dark")
        theme_input.addItem("Light", "light")
        theme_input.setCurrentIndex(max(0, theme_input.findData(self.visual_settings["theme"])))

        slot_height_input = QSpinBox()
        slot_height_input.setRange(30, 64)
        slot_height_input.setSuffix(" px")
        slot_height_input.setValue(self.visual_settings["slot_height"])

        details_width_input = QSpinBox()
        details_width_input.setRange(320, 560)
        details_width_input.setSuffix(" px")
        details_width_input.setValue(self.visual_settings["details_panel_width"])

        time_font_input = QSpinBox()
        time_font_input.setRange(16, 32)
        time_font_input.setSuffix(" px")
        time_font_input.setValue(self.visual_settings["time_font_size"])

        event_title_font_input = QSpinBox()
        event_title_font_input.setRange(12, 24)
        event_title_font_input.setSuffix(" px")
        event_title_font_input.setValue(self.visual_settings["event_title_font_size"])

        time_axis_font_input = QSpinBox()
        time_axis_font_input.setRange(12, 22)
        time_axis_font_input.setSuffix(" px")
        time_axis_font_input.setValue(self.visual_settings["time_axis_font_size"])

        selected_border_input = QSpinBox()
        selected_border_input.setRange(1, 6)
        selected_border_input.setSuffix(" px")
        selected_border_input.setValue(self.visual_settings["selected_border_width"])

        note_marker_size_input = QSpinBox()
        note_marker_size_input.setRange(14, 28)
        note_marker_size_input.setSuffix(" px")
        note_marker_size_input.setValue(self.visual_settings["note_marker_size"])

        note_markers_input = QCheckBox()
        note_markers_input.setChecked(self.visual_settings["show_note_markers"])

        form_layout = QFormLayout()
        form_layout.addRow("Theme", theme_input)
        form_layout.addRow("Calendar row height", slot_height_input)
        form_layout.addRow("Right panel width", details_width_input)
        form_layout.addRow("Time font size", time_font_input)
        form_layout.addRow("Event title font size", event_title_font_input)
        form_layout.addRow("Time axis font size", time_axis_font_input)
        form_layout.addRow("Selected border width", selected_border_input)
        form_layout.addRow("Note marker size", note_marker_size_input)
        form_layout.addRow("Show note markers", note_markers_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(buttons)
        dialog.setLayout(layout)

        if dialog.exec() != QDialog.Accepted:
            return

        self.visual_settings = {
            "theme": theme_input.currentData(),
            "slot_height": slot_height_input.value(),
            "details_panel_width": details_width_input.value(),
            "time_font_size": time_font_input.value(),
            "event_title_font_size": event_title_font_input.value(),
            "time_axis_font_size": time_axis_font_input.value(),
            "selected_border_width": selected_border_input.value(),
            "note_marker_size": note_marker_size_input.value(),
            "show_note_markers": note_markers_input.isChecked(),
        }
        self.apply_visual_settings()

    def apply_visual_settings(self):
        self.setStyleSheet(application_style(self.visual_settings["theme"]))
        self.event_details_panel.setStyleSheet(details_panel_style(self.visual_settings["theme"]))
        self.event_details_panel.setFixedWidth(self.visual_settings["details_panel_width"])
        self.event_details_time.setStyleSheet(
            details_time_style(self.visual_settings["time_font_size"], self.visual_settings["theme"])
        )
        self.event_details_message.setStyleSheet(details_message_style(self.visual_settings["theme"]))
        self.event_details_status.set_theme(self.visual_settings["theme"])
        self.calendar_header.set_theme(self.visual_settings["theme"])
        self.month_calendar.set_theme(self.visual_settings["theme"])
        self.calendar_grid.apply_visual_settings(
            self.visual_settings["slot_height"],
            self.visual_settings["time_font_size"],
            self.visual_settings["event_title_font_size"],
            self.visual_settings["time_axis_font_size"],
            self.visual_settings["selected_border_width"],
            self.visual_settings["note_marker_size"],
            self.visual_settings["show_note_markers"],
            self.visual_settings["theme"],
        )
        self.update_calendar_header_padding()
