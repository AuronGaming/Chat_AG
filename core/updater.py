"""Модуль автообновления Chat_AG"""

import os
import sys
import json
import urllib.request
import urllib.error
import subprocess
import tempfile
from PyQt6.QtCore import QObject, pyqtSignal, QThread


def _get_github_token():
    """Получить токен из config.json (не хранится в Git)"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('github_token', '')
        except Exception as e:
            print(f"⚠️ Ошибка чтения config.json: {e}")
    return os.environ.get('GITHUB_TOKEN', '')


class Updater(QObject):
    """Проверка и установка обновлений"""

    update_available = pyqtSignal(str, str)
    update_downloaded = pyqtSignal(str)
    no_update = pyqtSignal()
    error_occurred = pyqtSignal(str)

    GITHUB_REPO = "AuronGaming/Chat_AG"

    def __init__(self):
        super().__init__()
        self.current_version = "1.0.1"
        self.github_token = _get_github_token()

    def check_for_updates(self):
        try:
            url = f"https://api.github.com/repos/{self.GITHUB_REPO}/releases/latest"
            headers = {"Accept": "application/vnd.github.v3+json"}

            if self.github_token:
                headers["Authorization"] = f"token {self.github_token}"

            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())

            latest_version = data.get("tag_name", "0.0.0").lstrip("v")
            assets = data.get("assets", [])

            installer_url = None
            for asset in assets:
                if asset.get("name", "").endswith(".exe"):
                    installer_url = asset.get("browser_download_url")
                    break

            if installer_url and self._is_newer_version(latest_version, self.current_version):
                print(f"🔄 Доступно обновление: {latest_version}")
                self.update_available.emit(latest_version, installer_url)
            else:
                print("✅ Обновлений нет")
                self.no_update.emit()

        except Exception as e:
            print(f"❌ Ошибка проверки обновлений: {e}")
            self.error_occurred.emit(str(e))

    def download_update(self, url: str):
        try:
            headers = {"Accept": "application/octet-stream"}
            if self.github_token:
                headers["Authorization"] = f"token {self.github_token}"

            req = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(req, timeout=60) as response:
                data = response.read()

            temp_dir = tempfile.gettempdir()
            installer_path = os.path.join(temp_dir, "Chat_AG_Updater.exe")

            with open(installer_path, "wb") as f:
                f.write(data)

            print(f"✅ Обновление скачано: {installer_path}")
            self.update_downloaded.emit(installer_path)

        except Exception as e:
            print(f"❌ Ошибка скачивания: {e}")
            self.error_occurred.emit(str(e))

    def install_update(self, installer_path: str):
        try:
            subprocess.Popen([installer_path], shell=True)
            print("🚀 Запуск установщика...")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Ошибка установки: {e}")
            self.error_occurred.emit(str(e))

    def _is_newer_version(self, latest: str, current: str) -> bool:
        try:
            latest_parts = [int(x) for x in latest.split(".")]
            current_parts = [int(x) for x in current.split(".")]
            return latest_parts > current_parts
        except:
            return False