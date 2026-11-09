"""Кастомный заголовок окна"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QPolygonF
from ui.theme_config import COLORS  # ← ВАЖНО: этот импорт был пропущен!


def create_update_icon(size=16) -> QIcon:
    """Создать иконку обновления: зелёная стрелка вверх на прозрачном фоне"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)  # Прозрачный фон

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Зелёная стрелка вверх
    painter.setPen(QPen(QColor("#2ea043"), max(1, size // 8), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    painter.setBrush(QColor("#2ea043"))

    # Вертикальная линия стрелки
    painter.drawLine(int(size * 0.5), int(size * 0.8), int(size * 0.5), int(size * 0.35))

    # Наконечник стрелки (треугольник)
    arrow = QPolygonF([
        QPointF(size * 0.5, size * 0.15),
        QPointF(size * 0.25, size * 0.45),
        QPointF(size * 0.75, size * 0.45)
    ])
    painter.drawPolygon(arrow)

    painter.end()
    return QIcon(pixmap)


class CustomTitleBar(QWidget):
    """Кастомный заголовок окна с кнопками управления"""

    def __init__(self, title: str, parent=None, show_extra_buttons: bool = True):
        super().__init__(parent)
        self.parent_window = parent

        self.setFixedHeight(40)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['bg_main']};
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 5, 0)
        layout.setSpacing(10)

        # Заголовок
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['accent']};
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(title_label)

        layout.addStretch()

        if show_extra_buttons:
            # Кнопка активации
            btn_activation = QPushButton("🔑")
            btn_activation.setFixedSize(30, 30)
            btn_activation.setStyleSheet(self._btn_style())
            btn_activation.clicked.connect(self._on_activation)
            layout.addWidget(btn_activation)

            # Кнопка настроек
            btn_settings = QPushButton("⚙")
            btn_settings.setFixedSize(30, 30)
            btn_settings.setStyleSheet(self._btn_style())
            btn_settings.clicked.connect(self._on_settings)
            layout.addWidget(btn_settings)

        # Кнопки управления окном
        btn_minimize = QPushButton("—")
        btn_minimize.setFixedSize(30, 30)
        btn_minimize.setStyleSheet(self._btn_style())
        btn_minimize.clicked.connect(self._on_minimize)
        layout.addWidget(btn_minimize)

        btn_maximize = QPushButton("□")
        btn_maximize.setFixedSize(30, 30)
        btn_maximize.setStyleSheet(self._btn_style())
        btn_maximize.clicked.connect(self._on_maximize)
        layout.addWidget(btn_maximize)

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(30, 30)
        btn_close.setStyleSheet(self._btn_style_close())
        btn_close.clicked.connect(self._on_close)
        layout.addWidget(btn_close)

    def _btn_style(self) -> str:
        """Единый стиль для всех кнопок: прозрачный фон + зелёная обводка"""
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['accent']};
                border-radius: 4px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent']}30;
            }}
        """

    def _btn_style_close(self) -> str:
        """Стиль для кнопки закрытия: зелёная обводка, но красный при наведении"""
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['accent']};
                border-radius: 4px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['error']};
                color: white;
                border-color: {COLORS['error']};
            }}
        """

    def _on_settings(self):
        if self.parent_window and hasattr(self.parent_window, 'open_settings'):
            self.parent_window.open_settings()

    def _on_activation(self):
        if self.parent_window and hasattr(self.parent_window, 'open_activation'):
            self.parent_window.open_activation()

    def _on_minimize(self):
        """Свернуть в трей"""
        if self.parent_window:
            self.parent_window.hide()
            print("📦 Окно свернуто в трей")

    def _on_maximize(self):
        if self.parent_window:
            if self.parent_window.isMaximized():
                self.parent_window.showNormal()
            else:
                self.parent_window.showMaximized()

    def _on_close(self):
        """Закрыть окно — вызывает closeEvent главного окна"""
        if self.parent_window:
            self.parent_window.close()

    def add_extra_button(self, button):
        """Добавить кнопку перед кнопками управления окном (рядом с 🔑 и ⚙)"""
        layout = self.layout()
        # Находим кнопку minimize (—) и вставляем перед ней
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), QPushButton):
                if item.widget().text() == "—":
                    layout.insertWidget(i, button)
                    return
        # Если не нашли, добавляем в конец
        layout.addWidget(button)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._on_maximize()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.parent_window:
                self.parent_window._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.parent_window:
            if hasattr(self.parent_window, '_drag_pos'):
                delta = event.globalPosition().toPoint() - self.parent_window._drag_pos
                self.parent_window.move(self.parent_window.pos() + delta)
                self.parent_window._drag_pos = event.globalPosition().toPoint()