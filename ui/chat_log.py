"""Виджет лога чата Chat_AG"""

from PyQt6.QtWidgets import QTextBrowser, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QDateTime, QRect
from PyQt6.QtGui import QTextCursor, QColor, QPainter, QPixmap, QFont, QImage
from PyQt6.QtCore import QByteArray, QBuffer
from base64 import b64encode
from ui.theme_config import COLORS
from ui.assets import create_platform_icon_large


class ChatLogWidget(QTextBrowser):
    """Виджет для отображения сообщений чата с иконками и временем"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setOpenExternalLinks(False)

        # Создаём паттерн-фон
        self._bg_pixmap = self._create_background_pattern(256)

        self.setStyleSheet(f"""
            QTextBrowser {{
                background-color: transparent;
                color: {COLORS['text_primary']};
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 8px;
            }}
            QTextBrowser::viewport {{
                background: transparent;
            }}
        """)

        # Устанавливаем фон через палитру
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(COLORS['bg_main']))
        self.setPalette(palette)

    def _create_background_pattern(self, size: int) -> QPixmap:
        """Создать паттерн-фон для чата как в RutonyChat"""
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor('#0d0d1a'))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Символы для паттерна
        symbols = ['🎮', '🎬', '🎤', '🎧', '📷', '🎥', '🎯', '🎲', '🎸', '🎺', '🕹️', '🎪']

        painter.setFont(QFont("Segoe UI Emoji", 14))

        grid_size = 4
        cell_size = size // grid_size

        for i in range(grid_size):
            for j in range(grid_size):
                x = cell_size * i + cell_size // 2 - 7
                y = cell_size * j + cell_size // 2 + 5

                symbol_idx = (i * grid_size + j) % len(symbols)
                symbol = symbols[symbol_idx]

                painter.setPen(QColor('#1a1a2e'))
                painter.drawText(x, y, symbol)

        painter.end()
        return pixmap

    def paintEvent(self, event):
        """Рисуем фон паттерном"""
        painter = QPainter(self.viewport())

        # Рисуем паттерн повторяющимся тайлом
        if not self._bg_pixmap.isNull():
            painter.setOpacity(0.3)
            x = 0
            while x < self.viewport().width():
                y = 0
                while y < self.viewport().height():
                    painter.drawPixmap(x, y, self._bg_pixmap)
                    y += self._bg_pixmap.height()
                x += self._bg_pixmap.width()
            painter.setOpacity(1.0)

        painter.end()

        # Рисуем текст поверх
        super().paintEvent(event)

    def _get_time(self) -> str:
        """Получить текущее время в формате ЧЧ:ММ"""
        return QDateTime.currentDateTime().toString("HH:mm")

    def _pixmap_to_base64(self, pixmap: QPixmap) -> str:
        """Конвертировать QPixmap в base64 строку"""
        image = QImage(pixmap.toImage())
        buffer = QByteArray()
        buf = QBuffer(buffer)
        buf.open(QBuffer.OpenModeFlag.WriteOnly)
        image.save(buf, "PNG")
        return b64encode(buffer.data()).decode('utf-8')

    def add_system_message(self, platform: str, message: str, level: str = "INFO"):
        """Добавить системное сообщение с иконкой платформы"""
        colors = {
            "INFO": COLORS['text_primary'],
            "SUCCESS": COLORS['accent'],
            "ERROR": COLORS['error'],
            "WARNING": "#ffaa00"
        }
        color = colors.get(level, COLORS['text_primary'])
        time_str = self._get_time()

        # Иконка платформы
        icon = create_platform_icon_large(platform.lower(), 14)
        pixmap = icon.pixmap(16, 16)
        b64 = self._pixmap_to_base64(pixmap)

        html = f'''
        <div style="margin: 2px 0;">
            <span style="color: {COLORS['text_secondary']}; font-size: 11px;">[{time_str}]</span>
            <img src="data:image/png;base64,{b64}" width="16" height="16" style="vertical-align: middle; margin: 0 4px;">
            <span style="color: {color}; font-weight: bold;">{platform}:</span>
            <span style="color: {color};"> {message}</span>
        </div>
        '''
        self.append(html)
        self._scroll_to_bottom()

    def add_chat_message(self, platform: str, username: str, message: str,
                         color: str = COLORS['text_primary'], badges: list = None,
                         emotes: dict = None, gifs: list = None):
        """Добавить сообщение из чата с иконкой и временем"""

        # ОТЛАДКА: показываем что пришло
        print(f"📥 ChatLog получил: platform='{platform}', username='{username}', message='{message}'")

        time_str = self._get_time()
        # ... остальной код без изменений

        # Иконка платформы
        icon = create_platform_icon_large(platform.lower(), 14)
        pixmap = icon.pixmap(16, 16)
        b64 = self._pixmap_to_base64(pixmap)

        # Бейджи
        badges_html = ""
        if badges:
            for badge in badges:
                badges_html += f'<span style="color:{COLORS["accent"]}; font-size:11px;">[{badge}]</span> '

        # Экранирование HTML
        safe_message = message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        html = f'''
        <div style="margin: 2px 0;">
            <span style="color: {COLORS['text_secondary']}; font-size: 11px;">[{time_str}]</span>
            <img src="data:image/png;base64,{b64}" width="16" height="16" style="vertical-align: middle; margin: 0 4px;">
            {badges_html}
            <span style="color: {color}; font-weight: bold;">{username}:</span>
            <span style="color: {COLORS['text_primary']};"> {safe_message}</span>
        </div>
        '''
        self.append(html)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        """Прокрутить вниз"""
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_log(self):
        """Очистить лог"""
        self.clear()