"""Настройки и TTS Chat_AG"""

from core.settings_manager import SettingsManager
from ui.close_dialog import CloseDialog


class MainWindowSettings:
    """Миксин для настроек и TTS"""

    def _init_tts(self):
        """Инициализировать TTS"""
        try:
            from tts.manager import TTSManager
            tts = TTSManager()
            s = SettingsManager()
            tts_settings = s.settings.get("tts", {})
            tts.enabled = tts_settings.get('enabled', False)
            tts.mute_chat = tts_settings.get('mute_chat', False)
            tts.mute_donate = tts_settings.get('mute_donate', False)
            voice_id = tts_settings.get('voice_id', '')
            if voice_id:
                tts.set_voice(voice_id)
            tts.set_volume(tts_settings.get('volume', 100) / 100.0)
            tts.set_rate(tts_settings.get('speed', 200))
            tts.set_template(tts_settings.get('template', '$text'))
            print(f"🔊 TTS инициализирован: enabled={tts.enabled}")
        except Exception as e:
            print(f"⚠️ Ошибка инициализации TTS: {e}")

    def open_settings(self):
        """Открыть окно настроек"""
        if not self.settings_window:
            from ui.settings_window import SettingsWindow
            self.settings_window = SettingsWindow(main_window=self)
            self.settings_window.settings_applied.connect(self._on_settings_applied)
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def open_activation(self):
        """Открыть окно активации"""
        print("🔑 Открытие окна активации...")

    def _on_settings_applied(self):
        """Настройки применены"""
        self.chat_log.add_system_message("Система", "Настройки применены, перезапуск платформ...", "INFO")
        self.platform_panel.reset_counters()

        # Обновить TTS
        try:
            from tts.manager import TTSManager
            tts = TTSManager()
            s = SettingsManager()
            tts_settings = s.settings.get("tts", {})
            tts.enabled = tts_settings.get('enabled', False)
            tts.mute_chat = tts_settings.get('mute_chat', False)
            tts.mute_donate = tts_settings.get('mute_donate', False)
            voice_id = tts_settings.get('voice_id', '')
            if voice_id:
                tts.set_voice(voice_id)
            tts.set_volume(tts_settings.get('volume', 100) / 100.0)
            tts.set_rate(tts_settings.get('speed', 200))
            tts.set_template(tts_settings.get('template', '$text'))
            print(f"🔊 TTS обновлён")
        except Exception as e:
            print(f"⚠️ Ошибка обновления TTS: {e}")

        # Перезапустить платформы
        for platform_name in list(self.active_workers.keys()):
            self._stop_platform(platform_name)

        if self.da_worker:
            self.da_worker.stop()
            self.da_worker = None

        self._load_and_start_platforms()
        self._load_donation_settings()

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        s = SettingsManager()
        saved_action = s.settings.get("close_action", "ask")

        if saved_action == "minimize":
            event.ignore()
            self.hide()
            if hasattr(self, 'tray_icon') and self.tray_icon:
                self.tray_icon.show()
            return
        elif saved_action == "exit":
            event.accept()
            return

        dialog = CloseDialog(self)
        if dialog.exec():
            choice = dialog.get_choice()
            if choice == "minimize":
                event.ignore()
                self.hide()
                if hasattr(self, 'tray_icon') and self.tray_icon:
                    self.tray_icon.show()
            else:
                event.accept()
        else:
            event.ignore()