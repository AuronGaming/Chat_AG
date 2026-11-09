"""Панель ввода сообщений"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QComboBox
from PyQt6.QtCore import pyqtSignal
from ui.theme_config import COLORS, INPUT_STYLE


class InputPanel(QWidget):
    """Панель для ввода и отправки сообщений"""

    send_clicked = pyqtSignal(str)
    platform_select_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['bg_main']};
                border-top: 1px solid {COLORS['border']};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        # Выбор платформы
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["Все платформы", "Twitch", "YouTube", "VK Play"])
        self.platform_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg_input']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 6px 10px;
                min-width: 140px;
            }}
            QComboBox:hover {{
                background-color: {COLORS['bg_hover']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
        """)
        self.platform_combo.currentTextChanged.connect(
            lambda text: self.platform_select_clicked.emit(text)
        )
        layout.addWidget(self.platform_combo)

        # Поле ввода
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Введите сообщение...")
        self.input_field.setStyleSheet(INPUT_STYLE)
        self.input_field.returnPressed.connect(self._on_send)
        layout.addWidget(self.input_field, stretch=1)

        # Кнопка отправки (зеленая)
        self.btn_send = QPushButton("▶")
        self.btn_send.setFixedSize(40, 36)
        self.btn_send.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #238636;
            }}
        """)
        self.btn_send.clicked.connect(lambda: self.send_clicked.emit(self.input_field.text()))
        layout.addWidget(self.btn_send)

        # Кнопки управления звуком (добавь этот блок)
        self.btn_mute_chat = QPushButton("🔊 Чат")
        self.btn_mute_chat.setFixedSize(70, 28)
        self.btn_mute_chat.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']}30;
                color: {COLORS['accent']};
                border: 1px solid {COLORS['accent']};
                border-radius: 4px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent']}50;
            }}
        """)
        layout.addWidget(self.btn_mute_chat)

        self.btn_mute_donate = QPushButton("🔊 Донат")
        self.btn_mute_donate.setFixedSize(70, 28)
        self.btn_mute_donate.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']}30;
                color: {COLORS['accent']};
                border: 1px solid {COLORS['accent']};
                border-radius: 4px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent']}50;
            }}
        """)
        layout.addWidget(self.btn_mute_donate)

    def _on_send(self):
        """Обработать отправку сообщения"""
        message = self.input_field.text().strip()
        if message:
            self.send_clicked.emit(message)
            self.input_field.clear()

    def get_selected_platform(self) -> str:
        """Получить выбранную платформу"""
        return self.platform_combo.currentText()