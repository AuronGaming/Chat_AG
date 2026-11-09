"""Twitch Worker - подключение к чату Twitch"""

import socket
import re
import time
from PyQt6.QtCore import QThread, pyqtSignal


class TwitchWorker(QThread):
    """Worker для подключения к чату Twitch"""

    connected = pyqtSignal(str)
    disconnected = pyqtSignal(str)
    message_received = pyqtSignal(str, str, str, dict, list)
    error_occurred = pyqtSignal(str)

    def __init__(self, platform_name: str, config: dict):
        super().__init__()
        self.platform_name = platform_name
        self.config = config

        self.nickname = config.get("nickname", "").lower()
        self.token = config.get("token", "").strip()
        self.channel = config.get("site", "").lower().lstrip("#").split("/")[-1]

        # Если токен пустой - используем анонимный
        if not self.token or self.token.lower() == "oauth:anonymous":
            self.token = "SCHMOOPIIE"
            self.is_anonymous = True
        else:
            # Добавляем oauth: если нет
            if not self.token.lower().startswith("oauth:"):
                self.token = "oauth:" + self.token
            self.is_anonymous = False

        self._is_running = False
        self.sock = None
        self.last_ping_time = time.time()

    def run(self):
        """Основной метод подключения"""
        self._is_running = True

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10.0)
            self.sock.connect(("irc.chat.twitch.tv", 6667))

            self.sock.send(f"PASS {self.token}\r\n".encode("utf-8"))
            self.sock.send(f"NICK {self.nickname}\r\n".encode("utf-8"))
            self.sock.send(f"JOIN #{self.channel}\r\n".encode("utf-8"))
            self.sock.send("CAP REQ :twitch.tv/tags\r\n".encode("utf-8"))

            self.connected.emit(self.channel)
            self.last_ping_time = time.time()

            print(f"🔗 Twitch подключен к #{self.channel} (анонимно: {self.is_anonymous})")

            buffer = ""
            ping_interval = 240  # PING каждые 4 минуты (Twitch требует < 5 мин)

            while self._is_running:
                try:
                    # Уменьшаем таймаут чтобы чаще проверять необходимость PING
                    self.sock.settimeout(1.0)
                    data = self.sock.recv(4096).decode("utf-8", errors="ignore")
                    if not data:
                        print("⚠️ Twitch: сервер закрыл соединение")
                        break

                    buffer += data
                    self.last_ping_time = time.time()

                    while "\r\n" in buffer:
                        line, buffer = buffer.split("\r\n", 1)
                        if line.strip():
                            self._parse_message(line)

                except socket.timeout:
                    # Проверяем нужно ли отправить PING
                    now = time.time()
                    if now - self.last_ping_time > ping_interval:
                        try:
                            print(f"🔄 Twitch PING (прошло {int(now - self.last_ping_time)} сек)")
                            self.sock.send("PING :tmi.twitch.tv\r\n".encode("utf-8"))
                            self.last_ping_time = now
                        except Exception as e:
                            print(f"⚠️ Twitch ошибка PING: {e}")
                            break
                except OSError:
                    break
                except Exception as e:
                    print(f"⚠️ Twitch ошибка чтения: {e}")
                    break

        except socket.timeout:
            self.error_occurred.emit("Таймаут подключения к Twitch")
        except ConnectionRefusedError:
            self.error_occurred.emit("Подключение отклонено Twitch")
        except Exception as e:
            self.error_occurred.emit(f"Ошибка подключения: {str(e)}")
        finally:
            self._cleanup()
            self.disconnected.emit(self.channel)

    def send_message(self, message: str):
        """Отправить сообщение в чат"""
        if self.sock and self._is_running:
            try:
                msg = f"PRIVMSG #{self.channel} :{message}\r\n"
                self.sock.send(msg.encode("utf-8"))
                print(f"📤 Twitch отправлено: {message}")
            except Exception as e:
                print(f"⚠️ Twitch ошибка отправки: {e}")
                self.error_occurred.emit(f"Не удалось отправить сообщение: {e}")
        else:
            print("⚠️ Twitch: нет подключения для отправки")

    def _parse_message(self, line: str):
        """Парсинг IRC сообщений"""
        if line.startswith("PING"):
            try:
                self.sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
            except:
                pass
            return

        if any(x in line for x in ["001 ", "002 ", "003 ", "004 ", "353 ", "366 ",
                                    "JOIN ", "PART ", "USERSTATE", "ROOMSTATE",
                                    "GLOBALUSERSTATE", "RECONNECT", "CAP "]):
            return

        if "NOTICE" in line:
            notice_match = re.search(r':([^ ]+) NOTICE \* :(.+)', line)
            if notice_match:
                self.error_occurred.emit(notice_match.group(2))
            return

        if "PRIVMSG" in line:
            try:
                username = "unknown"
                color = "#ffffff"
                message = ""
                emotes = {}
                gifs = []

                if line.startswith("@"):
                    tags_part, rest = line.split(" ", 1)

                    display_match = re.search(r'display-name=([^;]+)', tags_part)
                    if display_match and display_match.group(1):
                        username = display_match.group(1)
                    else:
                        user_match = re.search(r':([^!]+)!', rest)
                        if user_match:
                            username = user_match.group(1)

                    color_match = re.search(r'color=([^;]+)', tags_part)
                    if color_match and color_match.group(1) and color_match.group(1) != "":
                        color = color_match.group(1)
                    else:
                        color = self._get_username_color(username)

                    emotes_match = re.search(r'emotes=([^;]+)', tags_part)
                    if emotes_match and emotes_match.group(1) and emotes_match.group(1) != "/":
                        emotes_raw = emotes_match.group(1)
                        for emote_data in emotes_raw.split("/"):
                            if ":" in emote_data:
                                emote_id, positions = emote_data.split(":", 1)
                                emotes[emote_id] = []
                                for pos in positions.split(","):
                                    if "-" in pos:
                                        start, end = pos.split("-", 1)
                                        emotes[emote_id].append((int(start), int(end)))

                    if " :" in rest:
                        message = rest.split(" :", 1)[-1]
                else:
                    if " :" in line:
                        message = line.split(" :", 1)[-1]
                    user_match = re.search(r':([^!]+)!', line)
                    if user_match:
                        username = user_match.group(1)
                    color = self._get_username_color(username)

                if message and username:
                    print(f"💬 Twitch [{username}]: {message}")
                    self.message_received.emit(username, message, color, emotes, gifs)

            except Exception as e:
                print(f"⚠️ Twitch ошибка парсинга: {e}")

    def _get_username_color(self, username: str) -> str:
        """Генерация цвета для никнейма"""
        colors = [
            "#FF0000", "#0000FF", "#00FF00", "#B22222", "#FF7F50",
            "#9ACD32", "#FF4500", "#2E8B57", "#DAA520", "#D2691E",
            "#5F9EA0", "#1E90FF", "#FF69B4", "#8A2BE2", "#00FF7F"
        ]
        hash_val = sum(ord(c) for c in username) % len(colors)
        return colors[hash_val]

    def _cleanup(self):
        """Очистка ресурсов"""
        self._is_running = False
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                self.sock.close()
            except:
                pass
            self.sock = None

    def stop(self):
        """Остановить worker"""
        self._is_running = False
        self._cleanup()
        self.quit()
        self.wait(2000)