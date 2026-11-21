"""Менеджер TTS Chat_AG"""

from tts.worker import TTSWorker


class TTSManager:
    """Менеджер озвучки текста"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True

        self.enabled = False
        self.mute_chat = False
        self.mute_donate = False
        self.voice_id = ""
        self.volume = 100
        self.rate = 200
        self.template = "$text"

        self._worker = TTSWorker()
        self._worker.start()
        print("✅ TTSManager создан")

    def speak(self, text: str, is_donate: bool = False):
        """Озвучить текст"""
        if not self.enabled:
            return

        if is_donate and self.mute_donate:
            return

        if not is_donate and self.mute_chat:
            return

        self._worker.add_to_queue(text)

    def set_voice(self, voice_id: str):
        """Установить голос"""
        self.voice_id = voice_id
        self._worker.set_voice(voice_id)

    def set_volume(self, volume: float):
        """Установить громкость (0.0 - 1.0)"""
        self.volume = int(volume * 100)
        self._worker.set_volume(volume)

    def set_rate(self, rate: int):
        """Установить скорость речи"""
        self.rate = rate
        self._worker.set_rate(rate)

    def set_template(self, template: str):
        """Установить шаблон текста"""
        self.template = template
        self._worker.set_template(template)

    def stop(self):
        """Остановить TTS"""
        if self._worker:
            self._worker.stop()