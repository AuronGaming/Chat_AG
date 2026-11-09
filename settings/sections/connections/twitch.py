"""Настройки подключения к Twitch"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox
import webbrowser
from ui.theme_config import COLORS, INPUT_STYLE


class TwitchConnectionSection(QWidget):
    """Раздел настроек Twitch"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {COLORS['bg_main']};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(15, 15, 15, 15)
        lay.setSpacing(12)

        # Кнопки подключения
        btn_row = QHBoxLayout()

        btn_connect = QPushButton("🔗 Подключить")
        btn_connect.setStyleSheet(self._btn_style("#9146ff"))
        btn_connect.clicked.connect(lambda: webbrowser.open("https://www.twitch.tv/"))
        btn_row.addWidget(btn_connect, stretch=1)

        btn_token = QPushButton("🔑 Получить токен")
        btn_token.setStyleSheet(self._btn_style("#772ce8"))
        btn_token.clicked.connect(lambda: webbrowser.open("https://twitchtokengenerator.com/"))
        btn_row.addWidget(btn_token, stretch=1)

        lay.addLayout(btn_row)

        # Чекбокс и кнопка разлогиниться
        toggle_row = QHBoxLayout()

        self.enabled_checkbox = QCheckBox("Включить Twitch")
        self.enabled_checkbox.setStyleSheet(f"""
            QCheckBox {{ 
                color: {COLORS['text_primary']}; 
                font-size: 13px; 
                font-weight: bold;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 3px;
                background-color: {COLORS['bg_input']};
                border: 1px solid {COLORS['border']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['accent']};
            }}
        """)
        toggle_row.addWidget(self.enabled_checkbox)

        toggle_row.addStretch()

        btn_logout = QPushButton("🚪 Разлогиниться")
        btn_logout.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['error']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #cc0000;
            }}
        """)
        btn_logout.clicked.connect(self._logout)
        toggle_row.addWidget(btn_logout)

        lay.addLayout(toggle_row)

        # Поля ввода
        self.nickname = self._create_field("Никнейм:", "auron_gaming")
        self.url = self._create_field("URL канала:", "https://www.twitch.tv/auron_gaming")
        self.token = self._create_field("Токен:", "oauth:xxxxxxxxxxxxxxxxx", password=True)

        # Подсказка
        hint = QLabel("💡 Нажмите 'Подключить' чтобы открыть Twitch. Или 'Получить токен' для авторизации.")
        hint.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        lay.addWidget(hint)

        lay.addStretch()

    def _logout(self):
        """Разлогиниться — очистить все поля и выключить"""
        self.enabled_checkbox.setChecked(False)
        self.nickname.clear()
        self.url.clear()
        self.token.clear()
        print("🚪 Twitch: разлогинен")

    def _btn_style(self, color: str) -> str:
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {color}dd; }}
        """

    def _create_field(self, label: str, placeholder: str, password: bool = False) -> QLineEdit:
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {COLORS['text_primary']}; min-width: 100px; font-size: 13px;")
        row.addWidget(lbl)

        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setStyleSheet(INPUT_STYLE)
        if password:
            field.setEchoMode(QLineEdit.EchoMode.Password)
        row.addWidget(field, stretch=1)

        self.layout().addLayout(row)
        return field