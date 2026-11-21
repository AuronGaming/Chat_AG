"""Базовый класс для всех платформ"""

from PyQt6.QtCore import QThread, pyqtSignal


class BasePlatformWorker(QThread):
    """Базовый класс для worker'а платформы"""

    connected = pyqtSignal(str)
    disconnected = pyqtSignal(str)
    message_received = pyqtSignal(str, str, str, dict, list)
    error_occurred = pyqtSignal(str)

    def __init__(self, platform_name: str, config: dict):
        super().__init__()
        self.platform_name = platform_name
        self.config = config
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
        self.connected.emit(channel)

    def _emit_disconnected(self, channel: str):
        """Эмитировать событие отключения"""
        self.disconnected.emit(channel)

    def _emit_message(self, username: str, message: str, color: str,
                      emotes: dict = None, gifs: list = None):
        """Эмитировать событие сообщения"""
        self.message_received.emit(
            username, message, color,
            emotes or {}, gifs or []
        )

    def _emit_error(self, error: str):
        """Эмитировать событие ошибки"""
        self.error_occurred.emit(error)