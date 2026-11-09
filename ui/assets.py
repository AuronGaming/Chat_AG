"""Генератор иконок платформ Chat_AG — настоящие логотипы по образцам"""

from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QPolygonF, QPen, QPainterPath
from PyQt6.QtCore import Qt, QPointF, QRect


def create_platform_icon(platform: str, size=14) -> QIcon:
    """Создать иконку платформы по настоящему логотипу"""

    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

    s = size
    r = max(2, s // 5)  # радиус скругления

    if platform == 'twitch':
        # Twitch — фиолетовый квадрат со скруглениями
        painter.setBrush(QColor('#9146ff'))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, s, s, r, r)

        # Белый "пузырь речи" с вырезом
        painter.setBrush(QColor('white'))
        path = QPainterPath()
        path.moveTo(s * 0.2, s * 0.15)
        path.lineTo(s * 0.8, s * 0.15)
        path.lineTo(s * 0.8, s * 0.7)
        path.lineTo(s * 0.55, s * 0.7)
        path.lineTo(s * 0.45, s * 0.85)
        path.lineTo(s * 0.45, s * 0.7)
        path.lineTo(s * 0.2, s * 0.7)
        path.closeSubpath()
        painter.drawPath(path)

        # Два чёрных вертикальных прямоугольника (глаза) внутри пузыря
        painter.setBrush(QColor('#9146ff'))
        painter.setPen(Qt.PenStyle.NoPen)
        eye_w = max(1, int(s * 0.1))
        eye_h = max(2, int(s * 0.35))
        painter.fillRect(int(s * 0.35), int(s * 0.25), eye_w, eye_h, QColor('#9146ff'))
        painter.fillRect(int(s * 0.55), int(s * 0.25), eye_w, eye_h, QColor('#9146ff'))

    elif platform == 'youtube':
        # YouTube — красный квадрат со скруглениями и play
        painter.setBrush(QColor('#ff0000'))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, s, s, r, r)

        # Белый треугольник play
        triangle = QPolygonF([
            QPointF(s * 0.38, s * 0.25),
            QPointF(s * 0.38, s * 0.75),
            QPointF(s * 0.72, s * 0.5)
        ])
        painter.setBrush(QColor('white'))
        painter.drawPolygon(triangle)



    elif platform in ['vk', 'vk_play', 'vkplay', 'vk_video_live']:

        # VK Video Live — красный квадрат с надписью LIVE

        painter.setBrush(QColor('#ff3347'))  # Красный фон VK

        painter.setPen(Qt.PenStyle.NoPen)

        painter.drawRoundedRect(0, 0, s, s, r, r)

        # Синяя полоска слева

        painter.setBrush(QColor('#0077ff'))

        painter.drawRoundedRect(0, 2, max(1, s // 4), s - 4, 2, 2)

        # Белая надпись LIVE

        painter.setPen(QColor('white'))

        painter.setFont(QFont("Arial", max(4, s // 3), QFont.Weight.Bold))

        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "LIVE")

    elif platform == 'goodgame':
        # GoodGame — синий квадрат со скруглениями, "GG!!"
        painter.setBrush(QColor('#2b4ea0'))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, s, s, r, r)

        painter.setPen(QColor('white'))
        painter.setFont(QFont("Arial", max(6, s // 2), QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "GG")

    elif platform == 'kick':
        # Kick — чёрный квадрат со скруглениями, зелёная K
        painter.setBrush(QColor('#000000'))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, s, s, r, r)

        painter.setPen(QColor('#53fc18'))
        painter.setFont(QFont("Arial", max(6, s // 2), QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "K")

    elif platform == 'trovo':
        # Trovo — фиолетовый квадрат со скруглениями, T
        painter.setBrush(QColor('#7b2cbf'))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, s, s, r, r)

        painter.setPen(QColor('white'))
        painter.setFont(QFont("Arial", max(6, s // 2), QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "T")

    elif platform == 'rutube':
        # Rutube — красный квадрат со скруглениями, R
        painter.setBrush(QColor('#e30613'))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, s, s, r, r)

        painter.setPen(QColor('white'))
        painter.setFont(QFont("Arial", max(6, s // 2), QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "R")

    else:
        painter.setBrush(QColor('#888888'))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, s, s, r, r)

        painter.setPen(QColor('white'))
        painter.setFont(QFont("Arial", max(5, s // 3), QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "?")

    painter.end()
    return QIcon(pixmap)


def create_platform_icon_large(platform: str, size=16) -> QIcon:
    """Создать иконку для лога чата"""
    return create_platform_icon(platform, size)


def create_chat_background_pattern(size=100) -> QPixmap:
    """Создать мелкий паттерн-фон для чата как в RutonyChat"""
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor('#0a0a14'))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    symbols = ['🎮', '🎬', '🎤', '🎧', '📷', '🎥']

    painter.setFont(QFont("Segoe UI Emoji", 8))

    grid_size = 5
    cell_size = size // grid_size

    for i in range(grid_size):
        for j in range(grid_size):
            x = cell_size * i + cell_size // 2 - 4
            y = cell_size * j + cell_size // 2 + 3

            symbol_idx = (i * grid_size + j) % len(symbols)
            symbol = symbols[symbol_idx]

            painter.setPen(QColor('#151520'))
            painter.drawText(x, y, symbol)

    painter.end()
    return pixmap