"""Заглушка для разделов в разработке"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from ui.theme_config import COLORS


class PlaceholderSection(QWidget):
    def __init__(self, title: str):
        super().__init__()
        self.setStyleSheet(f"background-color: {COLORS['bg_main']};")
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(f"Раздел '{title}' в разработке или переносится"))