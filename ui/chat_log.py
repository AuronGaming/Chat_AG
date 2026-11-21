"""Виджет лога чата Chat_AG с иконками справа"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel
from PyQt6.QtCore import Qt, QDateTime
from ui.theme_config import COLORS


PLATFORM_COLORS = {
    "twitch": "#9146FF",
    "youtube": "#FF0000",
    "vk_play": "#0077FF",
    "donationalerts": "#FFD700",
    "Система": "#a0a0a0",
}

PLATFORM_ICONS = {
    "twitch": "🟣",
    "youtube": "🔴",
    "vk_play": "🔵",
    "donationalerts": "🟡",
    "Система": "⚙",
}


class ChatLogWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {COLORS['bg_main']};")

        # Основной layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Контейнер для чата (занимает всё пространство)
        chat_container = QWidget()
        chat_container.setStyleSheet(f"background-color: {COLORS['bg_main']};")
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(0, 0, 0, 0)

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_main']};
                color: {COLORS['text_primary']};
                border: none;
                font-size: 13px;
                padding: 5px;
            }}
            QScrollBar:vertical {{
                background-color: {COLORS['bg_secondary']};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLORS['border']};
                border-radius: 5px;
                min-height: 20px;
            }}
        """)
        chat_layout.addWidget(self.text_area)

        main_layout.addWidget(chat_container, stretch=1)

        # Узкая полоса справа с иконками (50px)
        right_panel = QWidget()
        right_panel.setFixedWidth(50)
        right_panel.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['bg_main']};
                border-left: 1px solid {COLORS['border']};
            }}
        """)

        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 10, 5, 10)
        right_layout.setSpacing(15)

        # Иконки в столбик
        icons = ["🎮", "🎬", "🎸", "🎬", "🎤", "🎯", "🎤", "🎤", "🎲", "🎧", "🎧"]
        for icon in icons:
            lbl = QLabel(icon)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    color: rgba(255, 255, 255, 30);
                    font-size: 20px;
                    font-family: "Segoe UI Emoji", "Segoe UI Symbol", "Apple Color Emoji";
                }
            """)
            right_layout.addWidget(lbl)

        right_layout.addStretch()
        main_layout.addWidget(right_panel)

    def add_chat_message(self, platform: str, username: str, message: str,
                         color: str = "#FFFFFF", emotes: dict = None, gifs: list = None):
        time = QDateTime.currentDateTime().toString("hh:mm")
        platform_color = PLATFORM_COLORS.get(platform.lower(), color)
        icon = PLATFORM_ICONS.get(platform.lower(), "💬")

        platform_tag = f'<span style="color: {platform_color}; font-weight: bold;">{icon} {platform}</span>'
        user_tag = f'<span style="color: {color}; font-weight: bold;">{username}</span>'

        html = f'''<div style="margin: 2px 0; padding: 2px 0;">
            <span style="color: {COLORS['text_secondary']}; font-size: 11px;">[{time}]</span>
            {platform_tag}: {user_tag}: {message}
        </div>'''

        self.text_area.append(html)
        self._scroll_to_bottom()

    def add_system_message(self, platform: str, message: str, level: str = "INFO"):
        time = QDateTime.currentDateTime().toString("hh:mm")
        colors = {
            "INFO": COLORS['text_secondary'],
            "SUCCESS": COLORS['success'],
            "WARNING": COLORS['warning'],
            "ERROR": COLORS['error'],
        }
        color = colors.get(level, COLORS['text_secondary'])
        icon = PLATFORM_ICONS.get(platform, "ℹ")

        platform_tag = f'<span style="color: {color}; font-weight: bold;">{icon} {platform}</span>'
        html = f'''<div style="margin: 2px 0;">
            <span style="color: {COLORS['text_secondary']}; font-size: 11px;">[{time}]</span>
            {platform_tag}: <span style="color: {color};">{message}</span>
        </div>'''

        self.text_area.append(html)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        scrollbar = self.text_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear(self):
        self.text_area.clear()