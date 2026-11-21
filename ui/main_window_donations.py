"""Управление DonationAlerts Chat_AG"""


class MainWindowDonations:
    """Миксин для работы с DonationAlerts"""

    def _connect_donation_alerts(self, token: str):
        """Подключиться к DonationAlerts"""
        if not token:
            print("⚠️ DonationAlerts: Токен не указан")
            return
        try:
            from platforms.donations.donation_alerts import DonationAlertsWorker
            config = {"token": token, "enabled": True}
            self.da_worker = DonationAlertsWorker(config)
            self.da_worker.donation_received.connect(self._on_donation_received)
            self.da_worker.chat_message.connect(self._on_chat_message)
            self.da_worker.platform_connected.connect(self._on_platform_connected)
            self.da_worker.platform_disconnected.connect(self._on_platform_disconnected)
            self.da_worker.platform_error.connect(self._on_platform_error)
            self.da_worker.start()
            print("✅ DonationAlerts: Запуск воркера...")
        except Exception as e:
            print(f"❌ DonationAlerts: Ошибка подключения: {e}")

    def _disconnect_donation_alerts(self):
        """Отключиться от DonationAlerts"""
        if hasattr(self, 'da_worker') and self.da_worker:
            self.da_worker.stop()
            self.da_worker = None
            print("🔌 DonationAlerts: Отключено")

    def _on_donation_received(self, platform: str, username: str, amount: float, currency: str, message: str):
        """Получен донат"""
        print(f"💰 Получен донат: {username} - {amount} {currency}")
        donate_text = f"💰 {username} задонатил {amount} {currency}"
        if message:
            donate_text += f": {message}"
        self.chat_log.add_chat_message(platform, "DONATION", donate_text, "#FFD700", emotes={}, gifs=[])

        try:
            from tts.manager import TTSManager
            tts = TTSManager()
            if tts.enabled and not tts.mute_donate:
                tts.speak(f"{username} задонатил {amount} {currency}. {message}", is_donate=True)
        except Exception as e:
            print(f"⚠️ Ошибка TTS для доната: {e}")

    def _load_donation_settings(self):
        """Загрузить настройки DonationAlerts"""
        from core.settings_manager import SettingsManager
        s = SettingsManager()
        connections = s.settings.get("connections", {})
        da_config = connections.get("donation_alerts", {})
        if da_config.get("enabled") and da_config.get("token"):
            print("🔄 DonationAlerts: Автоподключение по настройкам...")
            self._connect_donation_alerts(da_config["token"])