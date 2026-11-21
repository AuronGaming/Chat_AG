"""Кастомный заголовок окна с иконкой AG"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from ui.theme_config import COLORS
from ui.assets import create_ag_icon


class CustomTitleBar(QWidget):
    def __init__(self, title: str, parent=None, show_extra_buttons: bool = True):
        super().__init__(parent)
        self._parent_window = parent
        self.setFixedHeight(40)
        self.setStyleSheet(f"background-color: {COLORS['bg_main']}; border-bottom: 1px solid {COLORS['border']};")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 5, 0)
        layout.setSpacing(8)

        # Иконка AG
        self.icon_label = QLabel()
        self.icon_label.setPixmap(create_ag_icon(20).pixmap(20, 20))
        layout.addWidget(self.icon_label)

        # Заголовок
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"color: {COLORS['accent']}; font-size: 13px; font-weight: bold;")
        layout.addWidget(self.title_label, stretch=1)

        self.extra_buttons = []
        if show_extra_buttons and parent:
            if hasattr(parent, 'open_activation'):
                btn_key = self._create_icon_button("🔑")
                btn_key.clicked.connect(parent.open_activation)
                layout.addWidget(btn_key)
                self.extra_buttons.append(btn_key)

            if hasattr(parent, 'open_settings'):
                btn_settings = self._create_icon_button("⚙")
                btn_settings.clicked.connect(parent.open_settings)
                layout.addWidget(btn_settings)
                self.extra_buttons.append(btn_settings)

        btn_min = self._create_control_button("—")
        btn_min.clicked.connect(lambda: parent.showMinimized() if parent else None)
        layout.addWidget(btn_min)

        btn_max = self._create_control_button("☐")
        btn_max.clicked.connect(lambda: self._toggle_maximize(parent))
        layout.addWidget(btn_max)

        btn_close = self._create_control_button("✕", hover_color="#ff4444")
        btn_close.clicked.connect(lambda: parent.close() if parent else None)
        layout.addWidget(btn_close)

        self._is_maximized = False

    def _create_icon_button(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedSize(30, 30)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {COLORS['accent']};
                border-radius: 4px;
                color: {COLORS['accent']};
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent']}30;
            }}
        """)
        return btn

    def _create_control_button(self, text: str, hover_color: str = None) -> QPushButton:
        hc = hover_color or COLORS['accent']
        btn = QPushButton(text)
        btn.setFixedSize(30, 30)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                color: {COLORS['text_primary']};
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {hc}40;
                color: {hc};
            }}
        """)
        return btn

    def _toggle_maximize(self, parent):
        if parent:
            if self._is_maximized:
                parent.showNormal()
            else:
                parent.showMaximized()
            self._is_maximized = not self._is_maximized

    def add_extra_button(self, button: QPushButton):
        layout = self.layout()
        layout.insertWidget(layout.count() - 3, button)
        self.extra_buttons.append(button)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._parent_window:
                self._parent_window._drag_pos = event.globalPosition().toPoint() - self._parent_window.frameGeometry().topLeft()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._parent_window and self._parent_window._drag_pos:
            self._parent_window.move(event.globalPosition().toPoint() - self._parent_window._drag_pos)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._parent_window:
            self._parent_window._drag_pos = None
            event.accept()
            return
        super().mouseReleaseEvent(event)