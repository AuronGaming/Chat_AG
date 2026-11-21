"""Обработчики событий главного окна Chat_AG"""

from PyQt6.QtCore import Qt


class MainWindowHandlers:
    """Миксин для обработки событий"""

    def _connect_signals(self):
        """Подключить сигналы"""
        self.input_panel.send_clicked.connect(self._on_send_message)
        self.event_bus.chat_message.connect(self._on_chat_message)
        self.event_bus.system_message.connect(self._on_system_message)
        self.event_bus.platform_connected.connect(self._on_platform_connected)
        self.event_bus.platform_disconnected.connect(self._on_platform_disconnected)
        self.event_bus.platform_error.connect(self._on_platform_error)

    def _on_send_message(self, message: str):
        """Отправка сообщения"""
        platform = self.input_panel.get_selected_platform()
        if platform == "Все платформы":
            for worker in self.active_workers.values():
                worker.send_message(message)
        else:
            platform_key = platform.lower().replace(" ", "_")
            if platform_key in self.active_workers:
                self.active_workers[platform_key].send_message(message)
            else:
                self.chat_log.add_system_message("Ошибка", f"Платформа {platform} не подключена", "ERROR")

    def _on_chat_message(self, platform: str, username: str, message: str,
                         color: str, emotes: dict, gifs: list):
        """Обработка сообщения чата"""
        self.chat_log.add_chat_message(platform, username, message, color, emotes=emotes, gifs=gifs)
        platform_code = platform.upper()[:2]
        self.platform_panel.increment_counter(platform_code)

        try:
            from tts.manager import TTSManager
            tts = TTSManager()
            if tts.enabled and not tts.mute_chat:
                tts.speak(f"{username}: {message}", is_donate=False)
        except Exception as e:
            print(f"⚠️ Ошибка TTS: {e}")

    def _on_system_message(self, platform: str, message: str, level: str):
        """Обработка системного сообщения"""
        self.chat_log.add_system_message(platform, message, level)

    def _on_platform_connected(self, platform: str, channel: str):
        """Платформа подключилась"""
        self.chat_log.add_system_message(platform, f"Подключено к {channel}", "SUCCESS")
        self._update_platform_status(platform, True)
        self.status_bar.showMessage(f"Подключено: {platform}")

    def _on_platform_disconnected(self, platform: str, channel: str):
        """Платформа отключилась"""
        self.chat_log.add_system_message(platform, f"Отключено от {channel}", "WARNING")
        self._update_platform_status(platform, False)

    def _on_platform_error(self, platform: str, error: str):
        """Ошибка платформы"""
        self.chat_log.add_system_message(platform, error, "ERROR")

    def _update_platform_status(self, platform: str, active: bool):
        """Обновить статус платформы в панели (зелёная обводка)"""
        platform_code = platform.upper()[:2]
        if platform == "vk_play":
            platform_code = 'VK'
        elif platform == "donation_alerts":
            platform_code = 'DA'

        self.platform_panel.set_platform_active(platform_code, active)