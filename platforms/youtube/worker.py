"""YouTube Live Chat Worker"""

import re
import json
import time
import urllib.request
import urllib.error
from PyQt6.QtCore import QThread, pyqtSignal


class YoutubeWorker(QThread):
    connected = pyqtSignal(str)
    disconnected = pyqtSignal(str)
    message_received = pyqtSignal(str, str, str, dict, list)
    error_occurred = pyqtSignal(str)

    INNER_TUBE_API = "https://www.youtube.com/youtubei/v1"
    INNER_TUBE_KEY = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilwY9_11qcW8"
    INNER_TUBE_CLIENT = {
        "clientName": "WEB",
        "clientVersion": "2.20231121.00.00",
    }

    def __init__(self, platform_name: str, config: dict):
        super().__init__()
        self.platform_name = platform_name
        self.config = config
        self.channel_input = config.get("channel_id", "").strip()
        if not self.channel_input:
            self.channel_input = config.get("site", "").strip()
        self._is_running = False
        self._continuation_token = None
        self._video_id = None
        self._channel_name = ""
        self._seen_message_ids = set()
        self._seen_message_hashes = set()
        self._initial_fetch_done = False

    def run(self):
        print(f"🚀 YouTube worker запущен, channel_input={self.channel_input}")
        self._is_running = True
        try:
            self.error_occurred.emit("Поиск трансляции YouTube...")
            video_id, channel_name = self._find_livestream()
            if not video_id:
                self.error_occurred.emit("Активная трансляция не найдена")
                return
            self._video_id = video_id
            self._channel_name = channel_name or "YouTube"
            self.error_occurred.emit("Подключение к чату...")
            self._continuation_token = self._get_continuation_token(video_id)
            if not self._continuation_token:
                self.error_occurred.emit("Не удалось получить токен чата")
                return
            self.connected.emit(self._channel_name)
            print(f"🔗 YouTube подключен к чату {self._channel_name}")
            self._poll_chat()
        except Exception as e:
            self.error_occurred.emit(f"Ошибка подключения: {str(e)}")
            print(f"❌ YouTube ошибка: {e}")
        finally:
            self.disconnected.emit(self._channel_name or "YouTube")

    def _find_livestream(self):
        channel_id = self._extract_channel_id(self.channel_input)
        if not channel_id:
            if self.channel_input.startswith("http"):
                video_match = re.search(r'(?:v=|/live/|/shorts/)([a-zA-Z0-9_-]{11})', self.channel_input)
                if video_match:
                    return video_match.group(1), ""
            return None, ""
        print(f"🔍 Поиск livestream для: {channel_id}")
        if channel_id.startswith("@"):
            url = f"https://www.youtube.com/{channel_id}/live"
        elif channel_id.startswith("UC"):
            url = f"https://www.youtube.com/channel/{channel_id}/live"
        else:
            url = f"https://www.youtube.com/@{channel_id}/live"
        print(f"  🔗 URL: {url}")

        # Принудительно используем IPv4
        import socket
        old_getaddrinfo = socket.getaddrinfo

        def new_getaddrinfo(*args):
            results = old_getaddrinfo(*args)
            # Фильтруем только IPv4
            return [r for r in results if r[0] == socket.AF_INET]

        socket.getaddrinfo = new_getaddrinfo

        for attempt in range(3):
            try:
                print(f"  🔄 Попытка {attempt + 1}/3...")
                req = urllib.request.Request(
                    url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Accept-Language": "en-US,en;q=0.9",
                    }
                )
                with urllib.request.urlopen(req, timeout=30) as response:
                    html = response.read().decode("utf-8")
                video_match = re.search(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
                if video_match:
                    video_id = video_match.group(1)
                    print(f"✅ Найден livestream: {video_id}")
                    channel_match = re.search(r'"ownerChannelName":"([^"]+)"', html)
                    channel_name = channel_match.group(1) if channel_match else channel_id
                    # Восстанавливаем оригинальный getaddrinfo
                    socket.getaddrinfo = old_getaddrinfo
                    return video_id, channel_name
                else:
                    print(f"  ❌ videoId не найден")
                    break
            except Exception as e:
                print(f"  ⚠️ Ошибка попытки {attempt + 1}: {e}")
                if attempt < 2:
                    time.sleep(2)

        # Восстанавливаем оригинальный getaddrinfo
        socket.getaddrinfo = old_getaddrinfo
        return None, ""

    def _extract_channel_id(self, channel_input: str) -> str:
        if channel_input.startswith("http"):
            match = re.search(r'/channel/([a-zA-Z0-9_-]+)', channel_input)
            if match:
                return match.group(1)
            match = re.search(r'/@([a-zA-Z0-9_.-]+)', channel_input)
            if match:
                return "@" + match.group(1)
            match = re.search(r'/c/([a-zA-Z0-9_-]+)', channel_input)
            if match:
                return match.group(1)
            match = re.search(r'/user/([a-zA-Z0-9_-]+)', channel_input)
            if match:
                return match.group(1)
        return channel_input

    def _get_continuation_token(self, video_id: str) -> str:
        url = f"{self.INNER_TUBE_API}/next?key={self.INNER_TUBE_KEY}"
        payload = {
            "context": {"client": self.INNER_TUBE_CLIENT},
            "videoId": video_id,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
            contents = result.get("contents", {})
            two_col = contents.get("twoColumnWatchNextResults", {})
            conv = two_col.get("conversationBar", {})
            live_chat = conv.get("liveChatRenderer", {})
            if live_chat:
                continuations = live_chat.get("continuations", [])
                if continuations:
                    token = continuations[0].get("reloadContinuationData", {}).get("continuation", "")
                    if token:
                        return token
            engagement_panels = two_col.get("engagementPanels", [])
            for panel in engagement_panels:
                panel_renderer = panel.get("engagementPanelSectionListRenderer", {})
                content = panel_renderer.get("content", {})
                section = content.get("sectionListRenderer", {}).get("contents", [])
                for item in section:
                    item_content = item.get("itemSectionRenderer", {}).get("contents", [])
                    for content_item in item_content:
                        live_chat = content_item.get("liveChatRenderer", {})
                        if live_chat:
                            continuations = live_chat.get("continuations", [])
                            if continuations:
                                token = continuations[0].get("reloadContinuationData", {}).get("continuation", "")
                                if token:
                                    return token
            return ""
        except Exception as e:
            print(f"⚠️ YouTube ошибка токена: {e}")
            return ""

    def _poll_chat(self):
        while self._is_running and self._continuation_token:
            try:
                messages, new_token, is_initial = self._fetch_chat_messages(self._continuation_token)
                if new_token:
                    self._continuation_token = new_token
                if not is_initial:
                    for msg in messages:
                        if self._is_running:
                            print(f"💬 YouTube сообщение: {msg['author']}: {msg['message']}")
                            self.message_received.emit(
                                msg.get("author", "unknown"),
                                msg.get("message", ""),
                                msg.get("color", "#ffffff"),
                                {}, []
                            )
                else:
                    print(f"⏭️ Пропущено {len(messages)} старых сообщений")
                time.sleep(3)
            except Exception as e:
                print(f"⚠️ YouTube ошибка поллинга: {e}")
                time.sleep(5)

    def _fetch_chat_messages(self, continuation_token: str) -> tuple:
        url = f"{self.INNER_TUBE_API}/live_chat/get_live_chat?key={self.INNER_TUBE_KEY}"
        payload = {
            "context": {"client": self.INNER_TUBE_CLIENT},
            "continuation": continuation_token,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        messages = []
        new_token = ""
        is_initial = False
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
            continuations = result.get("continuationContents", {}).get("liveChatContinuation", {}).get("continuations", [])
            if continuations:
                timed = continuations[0].get("timedContinuationData", {})
                reload = continuations[0].get("reloadContinuationData", {})
                if timed.get("continuation"):
                    new_token = timed["continuation"]
                    is_initial = False
                elif reload.get("continuation"):
                    new_token = reload["continuation"]
                    is_initial = not self._initial_fetch_done
            else:
                is_initial = not self._initial_fetch_done
            if not self._initial_fetch_done:
                self._initial_fetch_done = True
                is_initial = True
            actions = result.get("continuationContents", {}).get("liveChatContinuation", {}).get("actions", [])
            for action in actions:
                renderer = action.get("addChatItemAction", {}).get("item", {})
                message_id = action.get("id", "")
                msg_renderer = renderer.get("liveChatTextMessageRenderer", {})
                if msg_renderer:
                    author = msg_renderer.get("authorName", {}).get("simpleText", "unknown")
                    runs = msg_renderer.get("message", {}).get("runs", [])
                    message_text = ""
                    for run in runs:
                        if "text" in run:
                            message_text += run["text"]
                    if message_text:
                        if message_id and message_id in self._seen_message_ids:
                            continue
                        msg_hash = f"{author}:{message_text}"
                        if msg_hash in self._seen_message_hashes:
                            continue
                        if message_id:
                            self._seen_message_ids.add(message_id)
                        self._seen_message_hashes.add(msg_hash)
                        messages.append({"author": author, "message": message_text, "color": "#ffffff"})
                paid_renderer = renderer.get("liveChatPaidMessageRenderer", {})
                if paid_renderer:
                    author = paid_renderer.get("authorName", {}).get("simpleText", "unknown")
                    runs = paid_renderer.get("message", {}).get("runs", [])
                    message_text = ""
                    for run in runs:
                        if "text" in run:
                            message_text += run["text"]
                    if message_text:
                        msg_hash = f"paid:{author}:{message_text}"
                        if msg_hash in self._seen_message_hashes:
                            continue
                        if message_id:
                            self._seen_message_ids.add(message_id)
                        self._seen_message_hashes.add(msg_hash)
                        messages.append({"author": f"💰 {author}", "message": message_text, "color": "#ffd700"})
        except Exception as e:
            print(f"⚠️ YouTube ошибка сообщений: {e}")
        return messages, new_token, is_initial

    def send_message(self, message: str):
        print("⚠️ YouTube: отправка не поддерживается без OAuth")
        self.error_occurred.emit("Отправка сообщений в YouTube чат недоступна")

    def stop(self):
        self._is_running = False
        self.quit()
        self.wait(2000)