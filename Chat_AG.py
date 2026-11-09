"""Точка входа Chat_AG"""

import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    """Главная функция запуска"""
    app = QApplication(sys.argv)
    app.setApplicationName("Chat_AG")
    app.setApplicationVersion("1.0.3")

    # Устанавливаем иконку приложения
    import os
    from PyQt6.QtGui import QIcon
    icon_path = os.path.join(os.path.dirname(__file__), 'chat_ag_icon.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        print(f"✅ Иконка приложения установлена: {icon_path}")
    else:
        print(f"⚠️ Иконка не найдена: {icon_path}")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()