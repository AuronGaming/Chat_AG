"""Диалог закрытия Chat_AG"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from ui.theme_config import COLORS


def create_ag_icon(size=64) -> QIcon:
    """Создать иконку AG: зелёные буквы на чёрном фоне"""
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    painter.fillRect(0, 0, size, size, QColor(0, 0, 0))

    painter.setPen(QColor("#2ea043"))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.setFont(QFont("Segoe UI", size // 3, QFont.Weight.Bold))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "AG")

    painter.end()
    return QIcon(pixmap)


class CloseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Закрытие программы")
        self.setFixedSize(450, 280)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setWindowIcon(create_ag_icon(64))

        from core.settings_manager import SettingsManager
        s = SettingsManager()
        self.saved_choice = s.settings.get("close_action", "ask")

        container = QWidget()
        container.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['bg_main']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        # Заголовок с иконкой
        header_layout = QHBoxLayout()

        icon_label = QLabel()
        icon_label.setPixmap(create_ag_icon(48).pixmap(48, 48))
        header_layout.addWidget(icon_label)

        title = QLabel("Закрытие программы")
        title.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['accent']};
                font-size: 20px;
                font-weight: bold;
            }}
        """)
        header_layout.addWidget(title, stretch=1)
        layout.addLayout(header_layout)

        # Подсказка
        hint = QLabel("Chat_AG продолжит работать в фоне,\nесли свернуть окно в трей.")
        hint.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_secondary']};
                font-size: 12px;
                padding: 8px;
                background-color: {COLORS['bg_input']};
                border-radius: 4px;
            }}
        """)
        hint.setWordWrap(True)
        layout.addWidget(hint)

        layout.addSpacing(10)

        # Кнопка 1: Свернуть в трей
        self.btn_minimize = QPushButton("📥 Свернуть в трей")
        self.btn_minimize.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_input']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 12px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
                border-color: {COLORS['accent']};
            }}
        """)
        self.btn_minimize.clicked.connect(lambda: self.done_with_choice("minimize"))
        layout.addWidget(self.btn_minimize)

        # Кнопка 2: Закрыть полностью
        self.btn_close = QPushButton("🚪 Закрыть полностью")
        self.btn_close.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_input']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 12px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
                border-color: {COLORS['accent']};
            }}
        """)
        self.btn_close.clicked.connect(lambda: self.done_with_choice("exit"))
        layout.addWidget(self.btn_close)

        # Чекбокс "Запомнить выбор"
        self.remember_checkbox = QCheckBox("Запомнить мой выбор")
        self.remember_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {COLORS['text_secondary']};
                font-size: 11px;
                spacing: 6px;
            }}
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
                border-radius: 3px;
                background-color: {COLORS['bg_input']};
                border: 1px solid {COLORS['border']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['accent']};
            }}
        """)

        if self.saved_choice != "ask":
            action_text = {
                "minimize": "сворачивать в трей",
                "exit": "закрывать полностью"
            }.get(self.saved_choice, "")
            self.remember_checkbox.setText(f"✓ Запомнено: всегда {action_text}")
            self.remember_checkbox.setChecked(True)

        layout.addWidget(self.remember_checkbox)

        # Кнопка отмены
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_secondary']};
                border: none;
                padding: 6px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                color: {COLORS['text_primary']};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)

        self.choice = None

    def done_with_choice(self, choice):
        self.choice = choice

        if self.remember_checkbox.isChecked():
            from core.settings_manager import SettingsManager
            s = SettingsManager()
            s.settings["close_action"] = choice
            s.save()
            print(f"💾 Запомнен выбор: {choice}")
        else:
            from core.settings_manager import SettingsManager
            s = SettingsManager()
            if "close_action" in s.settings:
                del s.settings["close_action"]
                s.save()
                print("🔄 Выбор сброшен - теперь буду спрашивать")

        self.accept()

    def get_choice(self):
        return self.choice