"""Настройки подключения к YouTube"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox
import webbrowser
from ui.theme_config import COLORS, INPUT_STYLE


class YouTubeConnectionSection(QWidget):
    """Раздел настроек YouTube"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {COLORS['bg_main']};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(15, 15, 15, 15)
        lay.setSpacing(12)

        # Кнопка открытия YouTube
        btn_row = QHBoxLayout()
        btn_connect = QPushButton(" Открыть YouTube")
        btn_connect.setStyleSheet(self._btn_style("#FF0000"))
        btn_connect.clicked.connect(lambda: webbrowser.open("https://www.youtube.com"))
        btn_row.addWidget(btn_connect, stretch=1)
        lay.addLayout(btn_row)

        self.enabled_checkbox = QCheckBox("Включить YouTube")
        self.enabled_checkbox.setStyleSheet(f"""
            QCheckBox {{ color: {COLORS['text_primary']}; font-size: 13px; font-weight: bold; spacing: 8px; }}
            QCheckBox::indicator {{ width: 16px; height: 16px; border-radius: 3px; background-color: {COLORS['bg_input']}; border: 1px solid {COLORS['border']}; }}
            QCheckBox::indicator:checked {{ background-color: {COLORS['accent']}; }}
        """)
        lay.addWidget(self.enabled_checkbox)

        self.channel_url = self._create_field("URL канала:", "https://www.youtube.com/@Auron_Gaming")
        self.api_key = self._create_field("API Key (опционально):", "", password=True)

        # Кнопка разлогиниться (как на Twitch)
        self.btn_logout = QPushButton("🚪 Разлогиниться")
        self.btn_logout.setStyleSheet(self._btn_style("#FF6B6B"))
        self.btn_logout.clicked.connect(self.logout)
        lay.addWidget(self.btn_logout)

        hint = QLabel("💡 Вставьте URL канала YouTube. Программа найдёт активную трансляцию автоматически.")
        hint.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        lay.addWidget(hint)

        hint2 = QLabel("⚠️ Отправка сообщений в чат YouTube недоступна без OAuth.")
        hint2.setStyleSheet(f"color: #FFA500; font-size: 11px;")
        lay.addWidget(hint2)

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

    def logout(self):
        """Очистить данные авторизации"""
        self.api_key.clear()
        self.channel_url.clear()
        print("🚪 YouTube: данные авторизации очищены")