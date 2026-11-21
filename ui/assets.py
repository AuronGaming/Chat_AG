"""Иконки Chat_AG"""

from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QIcon
from PyQt6.QtCore import Qt


def create_ag_icon(size: int = 32) -> QIcon:
    """Иконка AG: зелёные буквы на чёрном фоне"""
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    painter.setPen(QColor("#2ea043"))
    painter.setFont(QFont("Segoe UI", size // 2, QFont.Weight.Bold))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "AG")
    painter.end()

    return QIcon(pixmap)


def create_platform_icon(letter: str, color: str, size: int = 24) -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0, 0))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QColor(color))
    painter.setBrush(QColor(0, 0, 0))
    painter.drawEllipse(2, 2, size - 4, size - 4)
    painter.setPen(QColor(color))
    painter.setFont(QFont("Segoe UI", size // 2, QFont.Weight.Bold))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, letter)
    painter.end()

    return QIcon(pixmap)


def create_update_icon(size: int = 16) -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0, 0))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QColor("#2ea043"))
    painter.setFont(QFont("Segoe UI", size - 2, QFont.Weight.Bold))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "↻")
    painter.end()

    return QIcon(pixmap)


TWITCH_ICON = create_platform_icon("T", "#9146FF")
YOUTUBE_ICON = create_platform_icon("Y", "#FF0000")
VK_ICON = create_platform_icon("VK", "#0077FF")
DA_ICON = create_platform_icon("DA", "#FFD700")