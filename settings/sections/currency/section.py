"""Раздел настроек 'Валюта'"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from ui.theme_config import COLORS


class Section(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {COLORS['bg_main']};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(15, 10, 15, 10)

        title = QLabel("Валюта")
        title.setStyleSheet(f"font-size: 22px; color: {COLORS['accent']}; font-weight: bold;")
        lay.addWidget(title)

        sub = QLabel("Настройка валюты.")
        sub.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']}; padding-bottom: 10px;")
        lay.addWidget(sub)

        lay.addStretch()

    def save_data(self):
        print("💾 Настройки валюты сохранены")