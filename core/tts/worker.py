"""TTS worker для озвучки текста"""

import queue
import threading
import time
from PyQt6.QtCore import QThread, pyqtSignal


class TTSWorker(QThread):
    """Worker для озвучки текста в отдельном потоке"""

    speak_started = pyqtSignal(str)
    speak_finished = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._queue = queue.Queue()
        self._running = True
        self._voice_id = ""
        self._volume = 1.0
        self._rate = 200
        self._template = "$text"
        self._muted = False

    def set_voice(self, voice_id: str):
        self._voice_id = voice_id

    def set_volume(self, volume: float):
        self._volume = max(0.0, min(1.0, volume))

    def set_rate(self, rate: int):
        self._rate = rate

    def set_template(self, template: str):
        self._template = template

    def set_muted(self, muted: bool):
        self._muted = muted

    def add_to_queue(self, text: str):
        """Добавить текст в очередь озвучки"""
        if not self._muted and text.strip():
            self._queue.put(text)

    def run(self):
        """Основной цикл обработки очереди"""
        while self._running:
            try:
                text = self._queue.get(timeout=1)
                self._speak(text)
                self._queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                self.error_occurred.emit(str(e))

    def _speak(self, text: str):
        """Озвучить текст"""
        try:
            # Применяем шаблон
            formatted_text = self._template.replace("$text", text)
            self.speak_started.emit(formatted_text)

            # Здесь будет реальная озвучка через pyttsx3 или другой движок
            # Пока просто имитация
            print(f"🔊 Озвучка: {formatted_text}")
            time.sleep(len(formatted_text) * 0.05)  # Имитация времени озвучки

            self.speak_finished.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop(self):
        """Остановить worker"""
        self._running = False
        self._queue.put("")  # Разблокировать queue.get()
        self.quit()
        self.wait(2000)