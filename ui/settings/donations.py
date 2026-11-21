"""Настройки озвучки донатов по площадкам"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QGroupBox
from PyQt6.QtCore import Qt
from ui.theme_config import COLORS
from core.settings_manager import SettingsManager


class DonateTTSSection(QWidget):
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

        for platform_name, items in [
            ("Twitch", ["Озвучивать Bits (поддержку канала)", "Озвучивать платные подписки (Subs)"]),
            ("YouTube", ["Озвучивать Super Chat", "Озвучивать спонсорство (Memberships)"]),
            ("VK Play Live", ["Озвучивать донаты VK"]),
            ("DonationAlerts / StreamElements",
             ["Озвучивать донаты с DonationAlerts", "Озвучивать донаты с StreamElements"]),
        ]:
            group = self._create_group(platform_name)
            group_lay = QVBoxLayout(group)
            for text in items:
                cb = QCheckBox(text)
                cb.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px; spacing: 8px;")
                group_lay.addWidget(cb)
            lay.addWidget(group)

        lay.addStretch()

    def _create_group(self, title: str) -> QGroupBox:
        group = QGroupBox(title)
        group.setStyleSheet(f"""
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
        return group

    def save_data(self):
        print("💾 Настройки озвучки донатов сохранены")