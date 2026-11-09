"""Иконка в системном трее Chat_AG"""

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication, QMessageBox
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import Qt


def create_ag_icon(size=32) -> QIcon:
    """Создать иконку: зелёные буквы AG на чёрном фоне"""
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


class TrayIcon(QSystemTrayIcon):
    """Иконка в системном трее"""

    _instance = None

    def __new__(cls, main_window=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, main_window=None):
        if self._initialized:
            return
        self._initialized = True
        self._main_window = main_window
        super().__init__()

        self.setIcon(create_ag_icon(32))
        self.setToolTip("Chat_AG v1.0.0")

        # Создаем контекстное меню
        menu = QMenu()

        show_action = QAction("📺 Показать окно", main_window)
        show_action.triggered.connect(self._show_window)
        menu.addAction(show_action)

        settings_action = QAction("⚙️ Настройки", main_window)
        settings_action.triggered.connect(
            main_window.open_settings
            if main_window and hasattr(main_window, 'open_settings')
            else lambda: None
        )
        menu.addAction(settings_action)

        menu.addSeparator()

        # Пункт для сброса выбора закрытия
        reset_close_action = QAction("🔄 Сбросить выбор закрытия", main_window)
        reset_close_action.triggered.connect(self._reset_close_choice)
        menu.addAction(reset_close_action)

        menu.addSeparator()

        quit_action = QAction("🚪 Выйти", main_window)
        quit_action.triggered.connect(self._quit_app)
        menu.addAction(quit_action)

        self.setContextMenu(menu)
        self.activated.connect(self._on_activated)
        self.show()
        print("✅ Иконка в трее создана")

    def _on_activated(self, reason):
        """Обработка активации иконки в трее (клик)"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self._main_window and self._main_window.isVisible():
                self._main_window.hide()
            elif self._main_window:
                self._show_window()

    def _show_window(self):
        """Показать окно"""
        if self._main_window:
            self._main_window.show()
            self._main_window.raise_()
            self._main_window.activateWindow()

    def _reset_close_choice(self):
        """Сбрасывает запомненный выбор закрытия"""
        try:
            from core.settings_manager import SettingsManager
            s = SettingsManager()
            if "close_action" in s.settings:
                del s.settings["close_action"]
                s.save()
                print("💾 Выбор закрытия сброшен")

            QMessageBox.information(
                self._main_window,
                "Chat_AG",
                "✅ Выбор закрытия сброшен!\n\nТеперь при нажатии на крестик\nснова появится диалог с выбором."
            )
        except Exception as e:
            print(f"⚠️ Ошибка сброса: {e}")

    def _quit_app(self):
        """Полный и принудительный выход из приложения без вопросов"""
        print("🚪 Принудительный выход из приложения...")

        # Сбрасываем выбор закрытия, чтобы в следующий раз программа вела себя стандартно
        try:
            from core.settings_manager import SettingsManager
            s = SettingsManager()
            if "close_action" in s.settings:
                del s.settings["close_action"]
                s.save()
        except Exception:
            pass

        # Принудительно завершаем приложение
        QApplication.quit()

    @classmethod
    def cleanup(cls):
        if cls._instance:
            cls._instance.hide()
            cls._instance.deleteLater()
            cls._instance = None