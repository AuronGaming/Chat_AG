"""Панель ввода сообщений Chat_AG"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QComboBox
from PyQt6.QtCore import pyqtSignal
from ui.theme_config import COLORS


class InputPanel(QWidget):
    send_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {COLORS['bg_main']}; border-top: 1px solid {COLORS['border']};")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["Все платформы", "Twitch", "YouTube", "VK Play Live", "DonationAlerts"])
        self.platform_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg_input']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 13px;
                min-width: 150px;
            }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['bg_main']};
                color: {COLORS['text_primary']};
                selection-background-color: {COLORS['accent']};
            }}
        """)
        layout.addWidget(self.platform_combo)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Введите сообщение...")
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg_input']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 13px;
            }}
            QLineEdit:focus {{ border-color: {COLORS['accent']}; }}
        """)
        self.input_field.returnPressed.connect(self._on_send)
        layout.addWidget(self.input_field, stretch=1)

        self.btn_send = QPushButton("▶")
        self.btn_send.setFixedSize(40, 35)
        self.btn_send.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #238636; }}
        """)
        self.btn_send.clicked.connect(self._on_send)
        layout.addWidget(self.btn_send)

        self.btn_mute_chat = QPushButton("🔊 Чат")
        self.btn_mute_chat.setFixedSize(80, 35)
        self.btn_mute_chat.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']}30;
                color: {COLORS['accent']};
                border: 1px solid {COLORS['accent']};
                border-radius: 4px;
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: {COLORS['accent']}50; }}
        """)
        layout.addWidget(self.btn_mute_chat)

        self.btn_mute_donate = QPushButton("🔊 Донат")
        self.btn_mute_donate.setFixedSize(80, 35)
        self.btn_mute_donate.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']}30;
                color: {COLORS['accent']};
                border: 1px solid {COLORS['accent']};
                border-radius: 4px;
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: {COLORS['accent']}50; }}
        """)
        layout.addWidget(self.btn_mute_donate)

    def _on_send(self):
        text = self.input_field.text().strip()
        if text:
            self.send_clicked.emit(text)
            self.input_field.clear()

    def get_selected_platform(self) -> str:
        return self.platform_combo.currentText()