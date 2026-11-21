"""YouTube чат worker"""

import time
import urllib.request
import json
from PyQt6.QtCore import pyqtSignal
from platforms.base import BasePlatformWorker


class YoutubeWorker(BasePlatformWorker):
    def __init__(self, config: dict):
        super().__init__("youtube", config)
        self.api_key = config.get("api_key", "")
        self.channel_id = config.get("channel_id", "")
        self.live_chat_id = None
        self.next_page_token = None

    def run(self):
        if not self.api_key or not self.channel_id:
            self._emit_error("YouTube: Не заполнены настройки")
            return

        self._is_running = True

        # Получаем live_chat_id
        try:
            self.live_chat_id = self._get_live_chat_id()
            if not self.live_chat_id:
                self._emit_error("YouTube: Трансляция не найдена")
                return
            self._emit_connected(self.channel_id)
        except Exception as e:
            self._emit_error(f"YouTube ошибка: {e}")
            return

        # Основной цикл получения сообщений
        while self._is_running:
            try:
                self._poll_messages()
                time.sleep(5)
            except Exception as e:
                self._emit_error(f"YouTube poll: {e}")
                time.sleep(10)

        self._emit_disconnected(self.channel_id)

    def _get_live_chat_id(self) -> str:
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={self.channel_id}&eventType=live&type=video&key={self.api_key}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

        items = data.get("items", [])
        if not items:
            return None

        video_id = items[0]["id"]["videoId"]

        url = f"https://www.googleapis.com/youtube/v3/videos?part=liveStreamingDetails&id={video_id}&key={self.api_key}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

        items = data.get("items", [])
        if not items:
            return None

        return items[0].get("liveStreamingDetails", {}).get("activeLiveChatId")

    def _poll_messages(self):
        if not self.live_chat_id:
            return

        url = f"https://www.googleapis.com/youtube/v3/liveChat/messages?liveChatId={self.live_chat_id}&part=snippet,authorDetails&key={self.api_key}"
        if self.next_page_token:
            url += f"&pageToken={self.next_page_token}"

        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

        self.next_page_token = data.get("nextPageToken")
        polling_interval = data.get("pollingIntervalMillis", 5000) / 1000

        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            author = item.get("authorDetails", {})
            username = author.get("displayName", "Аноним")
            message = snippet.get("displayMessage", "")
            self._emit_message(username, message, "#FF0000")

        time.sleep(polling_interval)

    def send_message(self, message: str):
        self._emit_error("YouTube: Отправка сообщений недоступна через API")

    def stop(self):
        self._is_running = False
        self.quit()
        self.wait(2000)