"""Twitch чат worker"""

import socket
import ssl
import time
from PyQt6.QtCore import pyqtSignal
from platforms.base import BasePlatformWorker


class TwitchWorker(BasePlatformWorker):
    def __init__(self, config: dict):
        super().__init__("twitch", config)
        self.nickname = config.get("nickname", "")
        self.token = config.get("token", "")
        self.channel = config.get("channel", "")
        self.sock = None

    def run(self):
        if not self.nickname or not self.token or not self.channel:
            self._emit_error("Twitch: Не заполнены настройки")
            return

        self._is_running = True
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            context = ssl.create_default_context()
            self.sock = context.wrap_socket(self.sock, server_hostname="irc.chat.twitch.tv")
            self.sock.connect(("irc.chat.twitch.tv", 6697))

            self.sock.send(f"PASS oauth:{self.token}\r\n".encode("utf-8"))
            self.sock.send(f"NICK {self.nickname}\r\n".encode("utf-8"))
            self.sock.send(f"JOIN #{self.channel}\r\n".encode("utf-8"))

            self._emit_connected(self.channel)

            buffer = ""
            while self._is_running:
                try:
                    data = self.sock.recv(2048).decode("utf-8", errors="ignore")
                    if not data:
                        break
                    buffer += data
                    while "\r\n" in buffer:
                        line, buffer = buffer.split("\r\n", 1)
                        self._process_message(line)
                except socket.timeout:
                    continue
                except Exception as e:
                    self._emit_error(f"Twitch ошибка: {e}")
                    break

        except Exception as e:
            self._emit_error(f"Twitch подключение: {e}")
        finally:
            if self.sock:
                self.sock.close()
            self._emit_disconnected(self.channel)

    def _process_message(self, line: str):
        if line.startswith("PING"):
            self.sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
            return

        if "PRIVMSG" in line:
            try:
                username = line.split("!")[0][1:]
                message = line.split("PRIVMSG")[1].split(":", 1)[1]
                self._emit_message(username, message, "#9146FF")
            except Exception:
                pass

    def send_message(self, message: str):
        if self.sock:
            self.sock.send(f"PRIVMSG #{self.channel} :{message}\r\n".encode("utf-8"))

    def stop(self):
        self._is_running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        self.quit()
        self.wait(2000)