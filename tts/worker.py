"""Worker TTS — озвучка в отдельном потоке"""

from PyQt6.QtCore import QThread, pyqtSignal, QObject
from tts.manager import TTSManager


class TTSWorker(QObject):
    """Worker для озвучки сообщений"""

    started = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.manager = TTSManager()
        self._queue = []
        self._is_running = False

    def start(self):
        """Запустить worker"""
        self._is_running = True
        self.started.emit()
        print("🔊 TTS Worker запущен")

    def stop(self):
        """Остановить worker"""
        self._is_running = False
        self.finished.emit()
        print("🔊 TTS Worker остановлен")

    def add_to_queue(self, text: str, msg_type: str = "chat"):
        """Добавить текст в очередь озвучки"""
        if not self._is_running:
            return

        # Проверка mute
        if msg_type == "chat" and self.manager.mute_chat:
            return
        if msg_type == "donate" and self.manager.mute_donate:
            return

        self._queue.append(text)
        self._process_queue()

    def _process_queue(self):
        """Обработать очередь"""
        while self._queue and self._is_running:
            text = self._queue.pop(0)
            self.manager.speak(text)