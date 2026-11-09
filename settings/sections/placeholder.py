"""Заглушка для разделов настроек"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from ui.theme_config import COLORS


class PlaceholderSection(QWidget):
    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {COLORS['bg_main']};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(15, 10, 15, 10)

        title = QLabel(name)
        title.setStyleSheet(f"font-size: 22px; color: {COLORS['accent']}; font-weight: bold;")
        lay.addWidget(title)

        sub = QLabel("Этот раздел находится в разработке.")
        sub.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']}; padding-bottom: 10px;")
        lay.addWidget(sub)

    def save_data(self):
        print("💾 Заглушка: настройки сохранены")