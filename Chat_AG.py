"""Точка входа Chat_AG"""

import sys
import os
import traceback

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtGui import QIcon
    from ui.main_window import MainWindow

    def main():
        app = QApplication(sys.argv)
        app.setApplicationName("Chat_AG")
        app.setApplicationVersion("1.0.3")

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)

        icon_path = os.path.join(base_path, 'chat_ag_icon.ico')

        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
            print(f"✅ Иконка приложения установлена: {icon_path}")
        else:
            print(f"⚠️ Иконка не найдена: {icon_path}")

        window = MainWindow()
        window.setWindowIcon(QIcon(icon_path) if os.path.exists(icon_path) else QIcon())
        window.show()

        sys.exit(app.exec())

    if __name__ == "__main__":
        main()

except Exception as e:
    print("=" * 60)
    print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
    print("=" * 60)
    traceback.print_exc()
    input("\nНажмите Enter для выхода...")
    sys.exit(1)