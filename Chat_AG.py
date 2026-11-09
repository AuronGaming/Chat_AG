"""Точка входа Chat_AG"""

import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    """Главная функция запуска"""
    app = QApplication(sys.argv)
    app.setApplicationName("Chat_AG")
    app.setApplicationVersion("1.0.3")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()