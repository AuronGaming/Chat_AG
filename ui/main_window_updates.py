"""Автообновление Chat_AG"""

from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QThread
from core.updater import Updater


class MainWindowUpdates:
    """Миксин для автообновления"""

    def _check_updates(self):
        """Проверить обновления"""
        try:
            self.btn_update.setText("⏳")
            self.btn_update.setEnabled(False)
            self.updater = Updater()
            self.updater.update_available.connect(self._on_update_available)
            self.updater.no_update.connect(self._on_no_update)
            self.updater.error_occurred.connect(self._on_update_error)
            self.updater.update_downloaded.connect(self._on_update_downloaded)
            self.updater_thread = QThread()
            self.updater.moveToThread(self.updater_thread)
            self.updater_thread.started.connect(self.updater.check_for_updates)
            self.updater_thread.start()
        except Exception as e:
            print(f"⚠️ Ошибка проверки обновлений: {e}")
            self.btn_update.setText("🔄")
            self.btn_update.setEnabled(True)

    def _on_update_available(self, version: str, url: str):
        """Доступно обновление"""
        reply = QMessageBox.question(self, "Доступно обновление",
                                     f"Найдена версия {version}.\nСкачать и установить?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.btn_update.setText("⬇️")
            self.updater.download_update(url)
        else:
            self.btn_update.setText("🔄")
            self.btn_update.setEnabled(True)

    def _on_no_update(self):
        """Обновлений нет"""
        QMessageBox.information(self, "Chat_AG", "У вас последняя версия!")
        self.btn_update.setText("🔄")
        self.btn_update.setEnabled(True)

    def _on_update_error(self, error: str):
        """Ошибка обновления"""
        QMessageBox.critical(self, "Ошибка", f"Не удалось проверить обновления:\n{error}")
        self.btn_update.setText("🔄")
        self.btn_update.setEnabled(True)

    def _on_update_downloaded(self, path: str):
        """Обновление скачано"""
        self.updater.install_update(path)