"""Автообновление Chat_AG через GitHub"""

import os
import sys
import json
import urllib.request
import subprocess
from PyQt6.QtCore import QObject, pyqtSignal, QThread


class Updater(QObject):
    """Проверка и установка обновлений с GitHub"""

    update_available = pyqtSignal(str, str)  # version, url
    no_update = pyqtSignal()
    error_occurred = pyqtSignal(str)
    update_downloaded = pyqtSignal(str)  # path to installer

    GITHUB_REPO = "AuronGaming/Chat_AG"
    CURRENT_VERSION = "1.0.3"

    def __init__(self):
        super().__init__()

    def check_for_updates(self):
        """Проверить наличие обновлений на GitHub"""
        try:
            url = f"https://api.github.com/repos/{self.GITHUB_REPO}/releases/latest"
            req = urllib.request.Request(url, headers={"User-Agent": "Chat_AG"})

            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())

            latest_version = data.get("tag_name", "").lstrip("v")

            if self._compare_versions(latest_version, self.CURRENT_VERSION) > 0:
                # Нашли более новую версию
                assets = data.get("assets", [])
                installer_url = ""
                for asset in assets:
                    if asset.get("name", "").endswith(".exe"):
                        installer_url = asset.get("browser_download_url", "")
                        break

                if installer_url:
                    self.update_available.emit(latest_version, installer_url)
                else:
                    self.error_occurred.emit("Установщик не найден в релизе")
            else:
                self.no_update.emit()

        except Exception as e:
            self.error_occurred.emit(str(e))

    def download_update(self, url: str):
        """Скачать обновление"""
        try:
            temp_dir = os.path.join(os.getenv("TEMP"), "Chat_AG_update")
            os.makedirs(temp_dir, exist_ok=True)

            filename = url.split("/")[-1]
            filepath = os.path.join(temp_dir, filename)

            req = urllib.request.Request(url, headers={"User-Agent": "Chat_AG"})
            with urllib.request.urlopen(req, timeout=60) as response:
                with open(filepath, "wb") as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)

            self.update_downloaded.emit(filepath)

        except Exception as e:
            self.error_occurred.emit(f"Ошибка скачивания: {e}")

    def install_update(self, installer_path: str):
        """Запустить установщик"""
        try:
            if sys.platform == "win32":
                os.startfile(installer_path)
            else:
                subprocess.Popen([installer_path])

            # Закрываем текущее приложение
            from PyQt6.QtWidgets import QApplication
            QApplication.quit()

        except Exception as e:
            self.error_occurred.emit(f"Ошибка установки: {e}")

    def _compare_versions(self, v1: str, v2: str) -> int:
        """Сравнить версии (возвращает 1 если v1 > v2, -1 если v1 < v2, 0 если равны)"""
        try:
            parts1 = [int(x) for x in v1.split(".")]
            parts2 = [int(x) for x in v2.split(".")]

            for p1, p2 in zip(parts1, parts2):
                if p1 > p2:
                    return 1
                elif p1 < p2:
                    return -1

            if len(parts1) > len(parts2):
                return 1
            elif len(parts1) < len(parts2):
                return -1

            return 0
        except Exception:
            return 0