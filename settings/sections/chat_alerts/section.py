"""Раздел настроек 'Звуки событий'"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QGroupBox
from PyQt6.QtCore import Qt
from ui.theme_config import COLORS


class Section(QWidget):
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

        # Twitch события
        twitch_group = QGroupBox("Twitch")
        twitch_group.setStyleSheet(f"""
            QGroupBox {{
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-weight: bold;
                border: 1px solid {COLORS['border']};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        twitch_lay = QVBoxLayout(twitch_group)
        twitch_lay.setSpacing(8)

        self.cb_twitch_sub = QCheckBox("Звук при новой подписке (Sub)")
        self.cb_twitch_sub.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px; spacing: 8px;")
        twitch_lay.addWidget(self.cb_twitch_sub)

        self.cb_twitch_raid = QCheckBox("Звук при рейде (Raid)")
        self.cb_twitch_raid.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px; spacing: 8px;")
        twitch_lay.addWidget(self.cb_twitch_raid)

        self.cb_twitch_host = QCheckBox("Звук при хосте (Host)")
        self.cb_twitch_host.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px; spacing: 8px;")
        twitch_lay.addWidget(self.cb_twitch_host)

        lay.addWidget(twitch_group)

        # YouTube события
        youtube_group = QGroupBox("YouTube")
        youtube_group.setStyleSheet(f"""
            QGroupBox {{
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-weight: bold;
                border: 1px solid {COLORS['border']};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        youtube_lay = QVBoxLayout(youtube_group)
        youtube_lay.setSpacing(8)

        self.cb_youtube_member = QCheckBox("Звук при новом спонсоре")
        self.cb_youtube_member.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px; spacing: 8px;")
        youtube_lay.addWidget(self.cb_youtube_member)

        lay.addWidget(youtube_group)

        # Общие события
        general_group = QGroupBox("Общие")
        general_group.setStyleSheet(f"""
            QGroupBox {{
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-weight: bold;
                border: 1px solid {COLORS['border']};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        general_lay = QVBoxLayout(general_group)
        general_lay.setSpacing(8)

        self.cb_mention = QCheckBox("Звук при упоминании моего никнейма")
        self.cb_mention.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px; spacing: 8px;")
        general_lay.addWidget(self.cb_mention)

        self.cb_first_message = QCheckBox("Звук при первом сообщении зрителя")
        self.cb_first_message.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px; spacing: 8px;")
        general_lay.addWidget(self.cb_first_message)

        lay.addWidget(general_group)

        lay.addStretch()

    def save_data(self):
        from core.settings_manager import SettingsManager
        s = SettingsManager()
        sounds = s.settings.get("event_sounds", {})
        sounds['twitch_sub'] = self.cb_twitch_sub.isChecked()
        sounds['twitch_raid'] = self.cb_twitch_raid.isChecked()
        sounds['twitch_host'] = self.cb_twitch_host.isChecked()
        sounds['youtube_member'] = self.cb_youtube_member.isChecked()
        sounds['mention'] = self.cb_mention.isChecked()
        sounds['first_message'] = self.cb_first_message.isChecked()
        s.settings["event_sounds"] = sounds
        s.save()
        print("💾 Настройки звуков событий сохранены")