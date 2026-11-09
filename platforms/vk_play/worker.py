"""VK Video Live Chat Worker — WebSocket с правильным парсером"""

import re
import json
import time
import gzip
import asyncio
import urllib.request
import urllib.error
import http.cookiejar
from PyQt6.QtCore import QThread, pyqtSignal

try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False


class VkPlayWorker(QThread):
    connected = pyqtSignal(str)
    disconnected = pyqtSignal(str)
    message_received = pyqtSignal(str, str, str, dict, list)
    error_occurred = pyqtSignal(str)

    def __init__(self, platform_name: str, config: dict):
        super().__init__()
        self.platform_name = platform_name
        self.config = config

        self.username = config.get("username", "").strip()
        if not self.username:
            self.username = config.get("channel_id", "").strip()

        self.session_cookie = config.get("session_cookie", "").strip()

        if self.username.startswith("http"):
            match = re.search(r'live\.vkvideo\.ru/([a-zA-Z0-9_]+)', self.username)
            if match:
                self.username = match.group(1)

        self._is_running = False
        self._channel_id = None
        self._channel_name = ""
        self._websocket = None

    def run(self):
        print(f"🚀 VK Play worker запущен, username='{self.username}'")

        if not self.username:
            self.error_occurred.emit("Username не указан")
            return

        self._is_running = True

        try:
            self.error_occurred.emit("🔍 Поиск канала VK Video Live...")
            channel_id, channel_name = self._find_channel()

            if not channel_id:
                self.error_occurred.emit("❌ Канал не найден")
                return

            self._channel_id = channel_id
            self._channel_name = channel_name or self.username
            print(f"✅ Канал найден: ID={channel_id}, Name={channel_name}")

            self.error_occurred.emit("🔗 Подключение к чату...")

            if HAS_WEBSOCKETS:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._connect_websocket())
                loop.close()
            else:
                self.error_occurred.emit("❌ Установи: pip install websockets")

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(f"Ошибка: {str(e)}")
        finally:
            self.disconnected.emit(self._channel_name or "VK Video Live")

    def _find_channel(self):
        url = f"https://live.vkvideo.ru/{self.username}"
        print(f"🔍 Ищем канал: {url}")

        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept-Encoding": "gzip, deflate",
                }
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                raw_data = response.read()

            if raw_data.startswith(b'\x1f\x8b'):
                raw_data = gzip.decompress(raw_data)

            html = raw_data.decode("utf-8")
            print(f"  📄 HTML: {len(html)} символов")

            patterns = [
                rf'"id"\s*:\s*(\d+)[^}}]*"blogUrl"\s*:\s*"{re.escape(self.username)}"',
                rf'"blogUrl"\s*:\s*"{re.escape(self.username)}"[^}}]*"id"\s*:\s*(\d+)',
                r'"owner"\s*:\s*\{[^}]*"id"\s*:\s*(\d+)',
            ]

            for i, pattern in enumerate(patterns):
                match = re.search(pattern, html)
                if match:
                    channel_id = match.group(1)
                    print(f"  ✅ Паттерн {i+1}: id={channel_id}")
                    return channel_id, self.username

            return None, ""

        except Exception as e:
            print(f"  ⚠️ Ошибка: {e}")
            return None, ""

    async def _connect_websocket(self):
        ws_url = "wss://pubsub.vkplay.live/connection/websocket"

        try:
            ws_token = None
            if self.session_cookie:
                self.error_occurred.emit("🔑 Авторизация...")
                ws_token = await self._get_ws_token()
                if not ws_token:
                    print("  ⚠️ Не удалось получить токен")

            headers = {
                "Origin": "https://vkplay.live",
                "User-Agent": "Mozilla/5.0"
            }

            print(f"🔌 Подключение к WebSocket...")
            self._websocket = await websockets.connect(ws_url, additional_headers=headers)

            # Шаг 1: Авторизация
            if ws_token:
                auth_msg = {
                    "params": {"token": ws_token, "name": "js"},
                    "id": 1
                }
                print(f"  📤 Авторизация...")
                await self._websocket.send(json.dumps(auth_msg))

                try:
                    response = await asyncio.wait_for(self._websocket.recv(), timeout=5.0)
                    print(f"  📥 Ответ: {response[:150]}")
                except asyncio.TimeoutError:
                    print("  ⚠️ Таймаут")

            # Шаг 2: Подписка
            subscribe_msg = {
                "method": 1,
                "params": {"channel": f"public-chat:{self._channel_id}"},
                "id": 2
            }
            print(f"  📤 Подписка: {json.dumps(subscribe_msg)}")
            await self._websocket.send(json.dumps(subscribe_msg))

            try:
                response = await asyncio.wait_for(self._websocket.recv(), timeout=5.0)
                print(f"  📥 Ответ: {response[:150]}")
                if '"result"' in response:
                    print(f"  ✅ Подписка успешна!")
            except asyncio.TimeoutError:
                print("  ⚠️ Таймаут")

            self.connected.emit(self._channel_name)
            self.error_occurred.emit(f"✅ Подключено к чату {self._channel_name}!")

            # Шаг 3: Keep-alive
            asyncio.create_task(self._keep_alive())

            # Шаг 4: Чтение
            await self._read_messages()

        except Exception as e:
            print(f"❌ Ошибка WebSocket: {e}")
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(f"Ошибка: {str(e)}")
        finally:
            if self._websocket:
                await self._websocket.close()

    async def _keep_alive(self):
        print("  🔁 Keep-alive запущен")
        counter = 100
        while self._is_running:
            await asyncio.sleep(30)
            try:
                counter += 1
                ping_msg = {"method": 7, "id": counter}
                await self._websocket.send(json.dumps(ping_msg))
                print(f"  🔁 Ping #{counter}")
            except Exception as e:
                print(f"  ❌ Ошибка ping: {e}")
                break

    async def _read_messages(self):
        print("  📖 Чтение сообщений...")
        try:
            async for message in self._websocket:
                if not self._is_running:
                    break

                await self._parse_message(message)
        except Exception as e:
            print(f"❌ Ошибка чтения: {e}")

    async def _parse_message(self, raw_message: str):
        """Парсер с максимальным логированием"""
        try:
            data = json.loads(raw_message)

            # Проверяем структуру
            if "result" not in data:
                return

            result = data["result"]
            channel = result.get("channel", "")

            # Проверяем канал
            if f"public-chat:{self._channel_id}" not in channel:
                return

            # Извлекаем данные
            msg_data = result.get("data", {})
            if not msg_data:
                print(f"  ⚠️ Нет data в result")
                return

            inner_data = msg_data.get("data", {})
            if not inner_data:
                print(f"  ️ Нет inner data")
                return

            # Проверяем тип
            msg_type = inner_data.get("type", "")
            if msg_type != "message":
                print(f"  ⚠️ Тип не message: {msg_type}")
                return

            # Извлекаем сообщение
            message_content = inner_data.get("data", {})

            # Логируем ВСЮ структуру
            print(f"  🔍 message_content ключи: {list(message_content.keys())}")
            print(f"  🔍 message_content: {json.dumps(message_content, ensure_ascii=False)[:500]}")

            # Автор
            author = message_content.get("author", {})
            username = author.get("nick") or author.get("name") or "Аноним"
            print(f"  👤 Автор: {username}")

            # Текст сообщения
            text_parts = message_content.get("data", [])
            print(f"  📦 text_parts тип: {type(text_parts)}")
            print(f"  📦 text_parts: {json.dumps(text_parts, ensure_ascii=False)[:300]}")

            message_text = ""

            if isinstance(text_parts, list):
                for i, part in enumerate(text_parts):
                    print(f"    [{i}] part: {json.dumps(part, ensure_ascii=False)[:200]}")

                    if isinstance(part, dict):
                        part_type = part.get("type", "")
                        content = part.get("content", "")

                        print(f"      type={part_type}, content={content} (тип: {type(content)})")

                        if part_type == "text":
                            if isinstance(content, str):
                                try:
                                    # Пытаемся распарсить строку как JSON
                                    parsed_content = json.loads(content)
                                    if isinstance(parsed_content, list):
                                        for item in parsed_content:
                                            if isinstance(item, str):
                                                # Жесткая фильтрация мусора VK
                                                clean_item = item.strip()
                                                if clean_item and clean_item not in ["unstyled", "BLOCK_END", "\\3\\",
                                                                                     "[]"]:
                                                    message_text += clean_item
                                except json.JSONDecodeError:
                                    # Если это не JSON, просто берем строку, если она не мусор
                                    clean_content = content.strip()
                                    if clean_content and clean_content not in ["unstyled", "BLOCK_END", "\\3\\"]:
                                        message_text += clean_content
                            elif isinstance(content, list):
                                for item in content:
                                    if isinstance(item, str):
                                        clean_item = item.strip()
                                        if clean_item and clean_item not in ["unstyled", "BLOCK_END", "\\3\\"]:
                                            message_text += clean_item

            print(f"  💬 Итоговый текст: '{message_text}'")

            if message_text.strip():
                print(f"  ✅ ОТПРАВЛЯЕМ В UI: platform={self.platform_name}, username={username}, text='{message_text}'")
                self.message_received.emit(
                    self.platform_name,
                    self._channel_name,
                    username,
                    {"color": "#FFFFFF"},
                    [message_text]
                )
            else:
                print(f"  ❌ Текст пустой после очистки: '{message_text}'")
                print(f"  🔍 Сырые данные: {json.dumps(message_content, ensure_ascii=False)[:300]}")

        except json.JSONDecodeError:
            pass
        except Exception as e:
            print(f"❌ Ошибка парсинга: {e}")
            import traceback
            traceback.print_exc()

    async def _get_ws_token(self) -> str:
        url = "https://api.vkplay.live/v1/ws/connect"
        try:
            cookie_jar = http.cookiejar.CookieJar()
            for cookie in self.session_cookie.split(";"):
                if "=" in cookie:
                    name, value = cookie.split("=", 1)
                    cookie_jar.set_cookie(http.cookiejar.Cookie(
                        0, name.strip(), value.strip(), None, False,
                        ".vkplay.live", True, False, "/", True,
                        False, None, True, None, None, {}
                    ))

            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Origin": "https://vkplay.live",
                    "Referer": "https://vkplay.live/"
                }
            )

            with opener.open(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                token = data.get("token")
                print(f"  ✅ Токен: {token[:30]}..." if token else "  ❌ Токен не получен")
                return token

        except Exception as e:
            print(f"  ❌ Ошибка токена: {e}")
            return None

    def send_message(self, message: str):
        print("⚠️ VK Video Live: отправка недоступна")
        self.error_occurred.emit("Отправка сообщений недоступна")

    def stop(self):
        self._is_running = False
        if self._websocket:
            try:
                asyncio.get_event_loop().run_until_complete(self._websocket.close())
            except:
                pass
        self.quit()
        self.wait(2000)