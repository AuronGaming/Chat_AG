"""Управление платформами Chat_AG"""

from core.settings_manager import SettingsManager


class MainWindowPlatforms:
    """Миксин для управления платформами"""

    def _load_and_start_platforms(self):
        """Загрузить и запустить платформы из настроек"""
        settings = SettingsManager()
        connections = settings.settings.get("connections", {})
        for platform_name, config in connections.items():
            if platform_name == "donation_alerts":
                continue
            if isinstance(config, dict) and config.get("enabled", False):
                self._start_platform(platform_name, config)

    def _start_platform(self, platform_name: str, config: dict):
        """Запустить платформу"""
        try:
            module_name = f"platforms.{platform_name}.worker"
            import importlib
            module = importlib.import_module(module_name)

            class_name = platform_name.title().replace('_', '') + "Worker"
            worker_class = getattr(module, class_name)
            worker = worker_class(config)

            worker.connected.connect(lambda ch, p=platform_name: self.event_bus.platform_connected.emit(p, ch))
            worker.disconnected.connect(lambda ch, p=platform_name: self.event_bus.platform_disconnected.emit(p, ch))
            worker.message_received.connect(lambda *args, p=platform_name: self._handle_message(args, p))
            worker.error_occurred.connect(lambda err, p=platform_name: self.event_bus.platform_error.emit(p, err))

            worker.start()
            self.active_workers[platform_name] = worker
            self.chat_log.add_system_message(platform_name, f"Запуск {platform_name}...", "INFO")
        except ImportError:
            self.chat_log.add_system_message(platform_name, f"Модуль {platform_name} не найден", "ERROR")
        except Exception as e:
            self.chat_log.add_system_message(platform_name, f"Ошибка запуска: {e}", "ERROR")

    def _handle_message(self, args, platform_name: str):
        """Обработать сообщение от платформы"""
        if len(args) == 5:
            username, message, color, emotes, gifs = args
            self.event_bus.chat_message.emit(platform_name, username, message, color, emotes or {}, gifs or [])

    def _stop_platform(self, platform_name: str):
        """Остановить платформу"""
        if platform_name in self.active_workers:
            worker = self.active_workers[platform_name]
            worker.stop()
            del self.active_workers[platform_name]
            self.chat_log.add_system_message(platform_name, "Остановлен", "WARNING")