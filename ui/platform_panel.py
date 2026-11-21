"""Панель статусов платформ — точно как на скрине"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from ui.theme_config import COLORS


class PlatformPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.setStyleSheet(f"background-color: {COLORS['bg_secondary']}; border-top: 1px solid {COLORS['border']};")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        # Общий счётчик
        self.counter_label = QLabel("# 0")
        self.counter_label.setStyleSheet(self._label_style(COLORS['text_secondary'], COLORS['border'], 1))
        layout.addWidget(self.counter_label)

        # Платформы: U(twitch), Y(outube), VK, GG, K(ick), T(rovo), R(ooter)
        self.platforms = {
            'U': self._create_platform_counter('U', '#9146FF'),
            'Y': self._create_platform_counter('Y', '#FF0000'),
            'VK': self._create_platform_counter('VK', '#0077FF'),
            'GG': self._create_platform_counter('GG', '#FFD700'),
            'K': self._create_platform_counter('K', '#FF69B4'),
            'T': self._create_platform_counter('T', '#00FFFF'),
            'R': self._create_platform_counter('R', '#FF4500'),
        }

        for label in self.platforms.values():
            layout.addWidget(label)

        layout.addStretch()

        self.status_label = QLabel("Не подключено")
        self.status_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        layout.addWidget(self.status_label)

    def _label_style(self, text_color: str, border_color: str, border_width: int) -> str:
        return f"""
            QLabel {{
                background-color: {COLORS['bg_input']};
                color: {text_color};
                border: {border_width}px solid {border_color};
                border-radius: 3px;
                padding: 2px 6px;
                font-size: 11px;
                font-weight: bold;
            }}
        """

    def _create_platform_counter(self, code: str, color: str) -> QLabel:
        label = QLabel(f"{code} 0")
        label.setStyleSheet(self._label_style(COLORS['text_secondary'], COLORS['border'], 1))
        label.setProperty("platform_code", code)
        label.setProperty("count", 0)
        label.setProperty("active", False)
        label.setProperty("platform_color", color)
        return label

    def increment_counter(self, platform_code: str):
        if platform_code in self.platforms:
            label = self.platforms[platform_code]
            count = label.property("count") or 0
            count += 1
            label.setProperty("count", count)
            label.setText(f"{platform_code} {count}")

    def set_platform_active(self, platform_code: str, active: bool):
        """Зелёная обводка при подключении"""
        if platform_code in self.platforms:
            label = self.platforms[platform_code]
            label.setProperty("active", active)
            if active:
                label.setStyleSheet(self._label_style(COLORS['text_primary'], COLORS['accent'], 2))
            else:
                color = label.property("platform_color") or COLORS['border']
                label.setStyleSheet(self._label_style(COLORS['text_secondary'], COLORS['border'], 1))

    def reset_counters(self):
        for label in self.platforms.values():
            label.setProperty("count", 0)
            code = label.property("platform_code")
            label.setText(f"{code} 0")
        self.counter_label.setText("# 0")