"""Базовый класс для всех платформ"""

from PyQt6.QtCore import QThread, QObject
from core.event_bus import EventBus


class BasePlatformWorker(QThread):
    """Базовый класс для worker'а платформы"""

    def __init__(self, platform_name: str, config: dict):
        super().__init__()
        self.platform_name = platform_name
        self.config = config
        self.event_bus = EventBus()
        self._is_running = False

    def run(self):
        """Основной метод подключения к платформе"""
        raise NotImplementedError("Метод run() должен быть реализован в наследнике")

    def send_message(self, message: str):
        """Отправить сообщение в чат платформы"""
        raise NotImplementedError("Метод send_message() должен быть реализован в наследнике")

    def stop(self):
        """Остановить worker"""
        self._is_running = False
        self.quit()
        self.wait(2000)

    def _emit_connected(self, channel: str):
        """Эмитировать событие подключения"""
        self.event_bus.platform_connected.emit(self.platform_name, channel)

    def _emit_disconnected(self, channel: str):
        """Эмитировать событие отключения"""
        self.event_bus.platform_disconnected.emit(self.platform_name, channel)

    def _emit_message(self, username: str, message: str, color: str,
                      emotes: dict = None, gifs: list = None):
        """Эмитировать событие сообщения"""
        self.event_bus.chat_message.emit(
            self.platform_name, username, message, color,
            emotes or {}, gifs or []
        )

    def _emit_error(self, error: str):
        """Эмитировать событие ошибки"""
        self.event_bus.platform_error.emit(self.platform_name, error)