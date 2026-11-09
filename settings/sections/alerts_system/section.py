"""Раздел настроек 'Озвучка донатов'"""

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

        title = QLabel("Озвучка донатов")
        title.setStyleSheet(f"font-size: 22px; color: {COLORS['accent']}; font-weight: bold;")
        lay.addWidget(title)

        sub = QLabel("Настройка озвучивания донатов с разных платформ и сервисов.")
        sub.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']}; padding-bottom: 10px;")
        lay.addWidget(sub)

        # Twitch донаты
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

        self.cb_twitch_bits = QCheckBox("Озвучивать Bits (поддержку канала)")
        self.cb_twitch_bits.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px; spacing: 8px;")
        twitch_lay.addWidget(self.cb_twitch_bits)

        self.cb_twitch_sub = QCheckBox("Озвучивать платные подписки (Subs)")
        self.cb_twitch_sub.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px; spacing: 8px;")
        twitch_lay.addWidget(self.cb_twitch_sub)

        lay.addWidget(twitch_group)

        # YouTube донаты
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

        self.cb_youtube_superchat = QCheckBox("Озвучивать Super Chat")
        self.cb_youtube_superchat.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px; spacing: 8px;")
        youtube_lay.addWidget(self.cb_youtube_superchat)

        self.cb_youtube_membership = QCheckBox("Озвучивать спонсорство (Memberships)")
        self.cb_youtube_membership.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px; spacing: 8px;")
        youtube_lay.addWidget(self.cb_youtube_membership)

        lay.addWidget(youtube_group)

        # VK Play донаты
        vk_group = QGroupBox("VK Play Live")
        vk_group.setStyleSheet(f"""
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
        vk_lay = QVBoxLayout(vk_group)
        vk_lay.setSpacing(8)

        self.cb_vk_donate = QCheckBox("Озвучивать донаты VK")
        self.cb_vk_donate.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px; spacing: 8px;")
        vk_lay.addWidget(self.cb_vk_donate)

        lay.addWidget(vk_group)

        # DonationAlerts (универсальный)
        da_group = QGroupBox("DonationAlerts / StreamElements")
        da_group.setStyleSheet(f"""
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
        da_lay = QVBoxLayout(da_group)
        da_lay.setSpacing(8)

        self.cb_da_donate = QCheckBox("Озвучивать донаты с DonationAlerts")
        self.cb_da_donate.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px; spacing: 8px;")
        da_lay.addWidget(self.cb_da_donate)

        self.cb_se_donate = QCheckBox("Озвучивать донаты с StreamElements")
        self.cb_se_donate.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px; spacing: 8px;")
        da_lay.addWidget(self.cb_se_donate)

        lay.addWidget(da_group)

        lay.addStretch()

    def save_data(self):
        from core.settings_manager import SettingsManager
        s = SettingsManager()
        donate_tts = s.settings.get("donate_tts", {})
        donate_tts['twitch_bits'] = self.cb_twitch_bits.isChecked()
        donate_tts['twitch_sub'] = self.cb_twitch_sub.isChecked()
        donate_tts['youtube_superchat'] = self.cb_youtube_superchat.isChecked()
        donate_tts['youtube_membership'] = self.cb_youtube_membership.isChecked()
        donate_tts['vk_donate'] = self.cb_vk_donate.isChecked()
        donate_tts['da_donate'] = self.cb_da_donate.isChecked()
        donate_tts['se_donate'] = self.cb_se_donate.isChecked()
        s.settings["donate_tts"] = donate_tts
        s.save()
        print("💾 Настройки озвучки донатов сохранены")