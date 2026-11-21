"""Диалог закрытия приложения Chat_AG"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QCheckBox, QHBoxLayout
from PyQt6.QtCore import Qt
from ui.theme_config import COLORS


class CloseDialog(QDialog):
    """Диалог выбора действия при закрытии"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Закрытие Chat_AG")
        self.setFixedSize(350, 200)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setStyleSheet(f"background-color: {COLORS['bg_main']};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Заголовок
        title = QLabel("Что сделать при закрытии?")
        title.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 16px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Кнопки выбора
        btn_minimize = QPushButton("📥 Свернуть в трей")
        btn_minimize.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_input']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 10px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent']}30;
                border-color: {COLORS['accent']};
            }}
        """)
        btn_minimize.clicked.connect(lambda: self._on_choice("minimize"))
        layout.addWidget(btn_minimize)

        btn_exit = QPushButton("🚪 Закрыть полностью")
        btn_exit.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_input']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 10px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['error']}30;
                border-color: {COLORS['error']};
            }}
        """)
        btn_exit.clicked.connect(lambda: self._on_choice("exit"))
        layout.addWidget(btn_exit)

        # Чекбокс запомнить выбор
        self.cb_remember = QCheckBox("Запомнить мой выбор")
        self.cb_remember.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(self.cb_remember)

        self._choice = None

    def _on_choice(self, choice: str):
        """Обработка выбора"""
        self._choice = choice

        if self.cb_remember.isChecked():
            try:
                from core.settings_manager import SettingsManager
                s = SettingsManager()
                s.settings["close_action"] = choice
                s.save()
                print(f"💾 Сохранён выбор закрытия: {choice}")
            except Exception as e:
                print(f"⚠️ Ошибка сохранения: {e}")

        self.accept()

    def get_choice(self) -> str:
        """Получить выбор пользователя"""
        return self._choice