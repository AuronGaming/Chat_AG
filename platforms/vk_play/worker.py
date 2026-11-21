"""VK Play Live чат worker"""

import time
import urllib.request
import json
from PyQt6.QtCore import pyqtSignal
from platforms.base import BasePlatformWorker


class VkPlayWorker(BasePlatformWorker):
    def __init__(self, config: dict):
        super().__init__("vk_play", config)
        self.login = config.get("login", "")
        self.password = config.get("password", "")
        self.channel_id = config.get("channel_id", "")
        self.access_token = None
        self.last_message_id = 0

    def run(self):
        if not self.login or not self.password or not self.channel_id:
            self._emit_error("VK Play: Не заполнены настройки")
            return

        self._is_running = True

        try:
            self.access_token = self._authorize()
            if not self.access_token:
                self._emit_error("VK Play: Ошибка авторизации")
                return

            self._emit_connected(self.channel_id)

            while self._is_running:
                try:
                    self._poll_messages()
                    time.sleep(3)
                except Exception as e:
                    self._emit_error(f"VK Play poll: {e}")
                    time.sleep(5)

        except Exception as e:
            self._emit_error(f"VK Play: {e}")
        finally:
            self._emit_disconnected(self.channel_id)

    def _authorize(self) -> str:
        url = "https://id.vk.com/oauth2/auth"
        data = json.dumps({
            "client_id": "vk_video_app",
            "client_secret": "",
            "grant_type": "password",
            "username": self.login,
            "password": self.password
        }).encode("utf-8")

        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode())
                return result.get("access_token", "")
        except Exception as e:
            print(f"⚠️ VK Play авторизация: {e}")
            return ""

    def _poll_messages(self):
        if not self.access_token:
            return

        url = f"https://api.vk.com/method/video.getLiveMessages?chat_id={self.channel_id}&access_token={self.access_token}&v=5.131"
        req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())

            items = data.get("response", {}).get("items", [])
            for item in items:
                msg_id = item.get("id", 0)
                if msg_id > self.last_message_id:
                    self.last_message_id = msg_id
                    username = item.get("from_id", "Аноним")
                    message = item.get("text", "")
                    self._emit_message(str(username), message, "#0077FF")
        except Exception as e:
            print(f"⚠️ VK Play poll: {e}")

    def send_message(self, message: str):
        self._emit_error("VK Play: Отправка сообщений недоступна")

    def stop(self):
        self._is_running = False
        self.quit()
        self.wait(2000)