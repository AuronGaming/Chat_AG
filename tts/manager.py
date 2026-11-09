"""Менеджер TTS Chat_AG — через SAPI5 напрямую, без pyttsx3"""

import threading
import queue
import time


class TTSManager:
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
        self.template = "$text"

        self.voices = []
        self.current_voice_index = 0
        self.volume = 100
        self.rate = 0

        self._queue = queue.Queue()
        self._running = True
        self._thread = None
        self._lock = threading.Lock()
        self._speaker = None

        self._init_voices()
        self._start_thread()
        print("✅ TTSManager готов")

    def _init_voices(self):
        try:
            import comtypes.client
            self._speaker = comtypes.client.CreateObject('SAPI.SpVoice')
            voice_tokens = self._speaker.GetVoices()

            self.voices = []
            for i in range(voice_tokens.Count):
                voice = voice_tokens.Item(i)
                self.voices.append((i, voice.GetDescription()))

            if self.voices:
                self.current_voice_index = 0

            print(f"🔊 Доступно голосов: {len(self.voices)}")
            for idx, name in self.voices:
                print(f"   [{idx}] {name}")

        except Exception as e:
            print(f"❌ Ошибка инициализации SAPI5: {e}")
            self.voices = []

    def _start_thread(self):
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._thread.start()
        print("🔊 TTS поток запущен")

    def _worker_loop(self):
        while self._running:
            try:
                text = self._queue.get(timeout=1.0)
                if text is None:
                    break

                with self._lock:
                    try:
                        if not self._speaker:
                            import comtypes.client
                            self._speaker = comtypes.client.CreateObject('SAPI.SpVoice')

                        voice_tokens = self._speaker.GetVoices()
                        if 0 <= self.current_voice_index < voice_tokens.Count:
                            self._speaker.Voice = voice_tokens.Item(self.current_voice_index)

                        self._speaker.Volume = self.volume
                        self._speaker.Rate = self.rate

                        # Синхронная озвучка
                        self._speaker.Speak(text, 1)

                    except Exception as e:
                        print(f"❌ Ошибка озвучки: {e}")
                        self._speaker = None

            except queue.Empty:
                continue

    def speak(self, text: str, is_donate: bool = False):
        if not self.enabled:
            return

        # Проверяем режимы mute
        if is_donate and self.mute_donate:
            return
        if not is_donate and self.mute_chat:
            return

        text = self.template.replace("$text", text)
        self._queue.put(text)

    def set_voice(self, voice_id: str):
        try:
            if ":" in voice_id:
                idx = int(voice_id.split(":")[0])
            else:
                idx = int(voice_id)
            self.current_voice_index = idx
        except:
            pass

    def set_volume(self, volume: float):
        self.volume = int(volume * 100)

    def set_rate(self, rate: int):
        self.rate = int((rate - 200) / 10)
        self.rate = max(-10, min(10, self.rate))

    def get_voices_list(self) -> list:
        return [(f"{idx}:{name}", name) for idx, name in self.voices]

    @classmethod
    def cleanup(cls):
        if cls._instance:
            cls._instance._running = False
            cls._instance._queue.put(None)
            cls._instance = None