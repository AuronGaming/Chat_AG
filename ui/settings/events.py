"""Настройки звуков событий в чате"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QGroupBox
from ui.theme_config import COLORS
from core.settings_manager import SettingsManager


class EventSoundsSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {COLORS['bg_main']};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(15, 10, 15, 10)
        lay.setSpacing(12)

        title = QLabel("Звуки событий")
        title.setStyleSheet(f"font-size: 22px; color: {COLORS['accent']}; font-weight: bold;")
        lay.addWidget(title)

        sub = QLabel("Звуковые сигналы при событиях в чате (подписки, хосты, рейды и т.д.).")
        sub.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']}; padding-bottom: 10px;")
        lay.addWidget(sub)

        general_group = QGroupBox("Общие события")
        general_group.setStyleSheet(
            f"color: {COLORS['text_primary']}; border: 1px solid {COLORS['border']}; border-radius: 5px; margin-top: 10px; padding-top: 15px;")
        general_lay = QVBoxLayout(general_group)

        self.cb_mention = QCheckBox("Звук при упоминании моего никнейма")
        self.cb_first_msg = QCheckBox("Звук при первом сообщении зрителя")
        for cb in [self.cb_mention, self.cb_first_msg]:
            cb.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px; spacing: 8px;")
            general_lay.addWidget(cb)
        lay.addWidget(general_group)

        lay.addStretch()

    def save_data(self):
        s = SettingsManager()
        sounds = s.settings.get("event_sounds", {})
        sounds['mention'] = self.cb_mention.isChecked()
        sounds['first_msg'] = self.cb_first_msg.isChecked()
        s.settings["event_sounds"] = sounds
        s.save()
        print("💾 Настройки звуков событий сохранены")