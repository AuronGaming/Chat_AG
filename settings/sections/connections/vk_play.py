"""Настройки подключения к VK Video Live"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox
import webbrowser
from ui.theme_config import COLORS, INPUT_STYLE


class VKConnectionSection(QWidget):
    """Раздел настроек VK Video Live"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {COLORS['bg_main']};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(15, 15, 15, 15)
        lay.setSpacing(12)

        btn_row = QHBoxLayout()
        btn_connect = QPushButton("🔗 Открыть VK Video Live")
        btn_connect.setStyleSheet(self._btn_style("#0077ff"))
        btn_connect.clicked.connect(lambda: webbrowser.open("https://live.vkvideo.ru/"))
        btn_row.addWidget(btn_connect, stretch=1)
        lay.addLayout(btn_row)

        self.enabled_checkbox = QCheckBox("Включить VK Video Live")
        self.enabled_checkbox.setStyleSheet(f"""
            QCheckBox {{ color: {COLORS['text_primary']}; font-size: 13px; font-weight: bold; spacing: 8px; }}
            QCheckBox::indicator {{ width: 16px; height: 16px; border-radius: 3px; background-color: {COLORS['bg_input']}; border: 1px solid {COLORS['border']}; }}
            QCheckBox::indicator:checked {{ background-color: {COLORS['accent']}; }}
        """)
        lay.addWidget(self.enabled_checkbox)

        self.username = self._create_field("Username канала:", "aurongaming")
        self.session_cookie = self._create_field("Cookie сессии (для чтения чата):", "vk_video_live_session=...; ld=...", password=True)

        hint = QLabel("💡 Для чтения чата скопируйте cookie из браузера (F12 → Application → Cookies → live.vkvideo.ru). Найдите 'vk_video_live_session' и 'ld'.")
        hint.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px; word-wrap: break-word;")
        hint.setWordWrap(True)
        lay.addWidget(hint)

        lay.addStretch()

    def _btn_style(self, color: str) -> str:
        return f"""
            QPushButton {{ background-color: {color}; color: white; border: none; border-radius: 6px; padding: 10px 16px; font-size: 14px; font-weight: bold; }}
            QPushButton:hover {{ background-color: {color}dd; }}
        """

    def _create_field(self, label: str, placeholder: str, password: bool = False) -> QLineEdit:
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {COLORS['text_primary']}; min-width: 160px; font-size: 13px;")
        row.addWidget(lbl)

        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setStyleSheet(INPUT_STYLE)
        if password:
            field.setEchoMode(QLineEdit.EchoMode.Password)
        row.addWidget(field, stretch=1)

        self.layout().addLayout(row)
        return field