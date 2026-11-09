"""Точка входа Chat_AG"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.main_window import MainWindow


def main():
    """Главная функция запуска"""
    app = QApplication(sys.argv)
    app.setApplicationName("Chat_AG")
    app.setApplicationVersion("1.0.3")

    # Путь к иконке (работает и в разработке, и после сборки)
    if getattr(sys, 'frozen', False):
        # После сборки PyInstaller
        base_path = sys._MEIPASS
    else:
        # При запуске из PyCharm
        base_path = os.path.dirname(__file__)

    icon_path = os.path.join(base_path, 'chat_ag_icon.ico')

    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        print(f"✅ Иконка приложения установлена: {icon_path}")
    else:
        print(f"⚠️ Иконка не найдена: {icon_path}")

    window = MainWindow()
    window.setWindowIcon(QIcon(icon_path))
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()