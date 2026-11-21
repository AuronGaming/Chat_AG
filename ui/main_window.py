"""Главное окно Chat_AG — финальная версия"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStatusBar, QPushButton, QMessageBox
from PyQt6.QtCore import Qt, QThread, QSize
from ui.theme_config import COLORS


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("Chat_AG v1.0.3")
        self.resize(600, 400)
        self.setMinimumSize(300, 200)

        self.settings_window = None
        self._drag_pos = None
        self._is_resizing = False
        self._resize_start_pos = None
        self.active_workers = {}
        self.da_worker = None
        self.updater = None
        self.updater_thread = None

        # EventBus
        from core.event_bus import EventBus
        self.event_bus = EventBus(self)

        # UI
        self._init_ui()

        # Сигналы
        self._connect_signals()

        # TTS (ленивая инициализация)
        self._tts_ready = False

        # Платформы
        self._load_and_start_platforms()

        # DonationAlerts
        self._load_donation_settings()

    def _init_ui(self):
        central_widget = QWidget()
        central_widget.setStyleSheet(f"background-color: {COLORS['bg_main']};")
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Заголовок
        from ui.custom_title_bar import CustomTitleBar
        self.title_bar = CustomTitleBar("Chat_AG v1.0.3", self)
        main_layout.addWidget(self.title_bar)

        # Кнопка обновления
        from ui.assets import create_update_icon
        self.btn_update = QPushButton()
        self.btn_update.setIcon(create_update_icon(16))
        self.btn_update.setIconSize(QSize(16, 16))
        self.btn_update.setFixedSize(30, 30)
        self.btn_update.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {COLORS['accent']};
                border-radius: 4px;
                padding: 4px;
            }}
            QPushButton:hover {{ background-color: {COLORS['accent']}30; }}
        """)
        self.btn_update.clicked.connect(self._check_updates)
        self.btn_update.setToolTip("Проверить обновления")
        self.title_bar.add_extra_button(self.btn_update)

        # Лог чата
        from ui.chat_log import ChatLogWidget
        self.chat_log = ChatLogWidget()
        main_layout.addWidget(self.chat_log, stretch=1)

        # Панель ввода
        from ui.input_panel import InputPanel
        self.input_panel = InputPanel()
        main_layout.addWidget(self.input_panel)

        # Панель платформ
        from ui.platform_panel import PlatformPanel
        self.platform_panel = PlatformPanel()
        main_layout.addWidget(self.platform_panel)

        # Статус-бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {COLORS['bg_main']};
                color: {COLORS['text_secondary']};
                border-top: 1px solid {COLORS['border']};
                font-size: 12px;
            }}
        """)
        self.status_bar.showMessage("Готов к работе.")

        self.chat_log.add_system_message("Twitch", "Ожидание подключения...", "INFO")
        self.chat_log.add_system_message("Система", "Откройте ⚙ Настройки → Соединения", "INFO")

        # Resize handle
        self._init_resize()

        # Tray icon
        from ui.tray_icon import TrayIcon
        self.tray_icon = TrayIcon(self)

    def _init_resize(self):
        self._resize_handle = QWidget(self)
        self._resize_handle.setFixedSize(20, 20)
        self._resize_handle.setCursor(Qt.CursorShape.SizeFDiagCursor)
        self._resize_handle.setStyleSheet(f"""
            QWidget {{ background-color: transparent; border: none; }}
            QWidget:hover {{ background-color: {COLORS['accent']}40; border-radius: 3px; }}
        """)
        self._resize_handle.move(self.width() - 20, self.height() - 20)
        self._resize_handle.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, '_resize_handle'):
            self._resize_handle.move(self.width() - 20, self.height() - 20)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if hasattr(self, '_resize_handle') and self._resize_handle.geometry().contains(event.pos()):
                self._is_resizing = True
                self._resize_start_pos = event.globalPosition().toPoint()
            else:
                self._drag_pos = event.globalPosition().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            if hasattr(self, '_is_resizing') and self._is_resizing:
                delta = event.globalPosition().toPoint() - self._resize_start_pos
                new_width = max(self.minimumWidth(), self.width() + delta.x())
                new_height = max(self.minimumHeight(), self.height() + delta.y())
                self.resize(new_width, new_height)
                self._resize_start_pos = event.globalPosition().toPoint()
            elif hasattr(self, '_drag_pos'):
                delta = event.globalPosition().toPoint() - self._drag_pos
                self.move(self.pos() + delta)
                self._drag_pos = event.globalPosition().toPoint()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_resizing = False
            self._drag_pos = None
        super().mouseReleaseEvent(event)

    def _connect_signals(self):
        self.input_panel.send_clicked.connect(self._on_send_message)
        self.event_bus.chat_message.connect(self._on_chat_message)
        self.event_bus.system_message.connect(self._on_system_message)
        self.event_bus.platform_connected.connect(self._on_platform_connected)
        self.event_bus.platform_disconnected.connect(self._on_platform_disconnected)
        self.event_bus.platform_error.connect(self._on_platform_error)

    def _init_tts(self):
        """Ленивая инициализация TTS"""
        if self._tts_ready:
            return
        try:
            from tts.manager import TTSManager
            from core.settings_manager import SettingsManager
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
            self._tts_ready = True
            print(f"🔊 TTS: enabled={tts.enabled}")
        except Exception as e:
            print(f"❌ TTS ошибка: {e}")

    def _load_and_start_platforms(self):
        from core.settings_manager import SettingsManager
        settings = SettingsManager()
        connections = settings.settings.get("connections", {})
        for platform_name, config in connections.items():
            if platform_name == "donation_alerts":
                continue
            if isinstance(config, dict) and config.get("enabled", False):
                self._start_platform(platform_name, config)

    def _start_platform(self, platform_name: str, config: dict):
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
        except Exception as e:
            print(f"❌ Ошибка запуска {platform_name}: {e}")

    def _handle_message(self, args, platform_name: str):
        if len(args) == 5:
            username, message, color, emotes, gifs = args
            self.event_bus.chat_message.emit(platform_name, username, message, color, emotes or {}, gifs or [])

    def _stop_platform(self, platform_name: str):
        if platform_name in self.active_workers:
            worker = self.active_workers[platform_name]
            worker.stop()
            del self.active_workers[platform_name]

    def _on_send_message(self, message: str):
        platform = self.input_panel.get_selected_platform()
        if platform == "Все платформы":
            for worker in self.active_workers.values():
                worker.send_message(message)
        else:
            platform_key = platform.lower().replace(" ", "_")
            if platform_key in self.active_workers:
                self.active_workers[platform_key].send_message(message)

    def _on_chat_message(self, platform: str, username: str, message: str, color: str, emotes: dict, gifs: list):
        self.chat_log.add_chat_message(platform, username, message, color, emotes=emotes, gifs=gifs)
        platform_code = platform.upper()[:2]
        if platform == "vk_play":
            platform_code = 'VK'
        elif platform == "donation_alerts":
            platform_code = 'DA'
        self.platform_panel.increment_counter(platform_code)

        # Ленивая инициализация TTS при первом сообщении
        self._init_tts()

    def _on_system_message(self, platform: str, message: str, level: str):
        self.chat_log.add_system_message(platform, message, level)

    def _on_platform_connected(self, platform: str, channel: str):
        self.chat_log.add_system_message(platform, f"Подключено к {channel}", "SUCCESS")
        self._update_platform_status(platform, True)
        self.status_bar.showMessage(f"Подключено: {platform}")

    def _on_platform_disconnected(self, platform: str, channel: str):
        self.chat_log.add_system_message(platform, f"Отключено от {channel}", "WARNING")
        self._update_platform_status(platform, False)

    def _on_platform_error(self, platform: str, error: str):
        self.chat_log.add_system_message(platform, error, "ERROR")

    def _update_platform_status(self, platform: str, active: bool):
        platform_code = platform.upper()[:2]
        if platform == "vk_play":
            platform_code = 'VK'
        elif platform == "donation_alerts":
            platform_code = 'DA'
        self.platform_panel.set_platform_active(platform_code, active)

    def open_settings(self):
        if not self.settings_window:
            from ui.settings_window import SettingsWindow
            self.settings_window = SettingsWindow(main_window=self)
            self.settings_window.settings_applied.connect(self._on_settings_applied)
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def open_activation(self):
        print("🔑 Активация...")

    def _on_settings_applied(self):
        self.chat_log.add_system_message("Система", "Настройки применены", "INFO")
        self.platform_panel.reset_counters()
        for platform_name in list(self.active_workers.keys()):
            self._stop_platform(platform_name)
        if self.da_worker:
            self.da_worker.stop()
            self.da_worker = None
        self._load_and_start_platforms()
        self._load_donation_settings()

    def _connect_donation_alerts(self, token: str):
        if not token:
            return
        try:
            from platforms.donations.donation_alerts import DonationAlertsWorker
            config = {"token": token, "enabled": True}
            self.da_worker = DonationAlertsWorker(config)
            self.da_worker.donation_received.connect(self._on_donation_received)
            self.da_worker.chat_message.connect(self._on_chat_message)
            self.da_worker.platform_connected.connect(
                lambda ch: self.event_bus.platform_connected.emit("donation_alerts", ch)
            )
            self.da_worker.platform_disconnected.connect(
                lambda ch: self.event_bus.platform_disconnected.emit("donation_alerts", ch)
            )
            self.da_worker.platform_error.connect(
                lambda err: self.event_bus.platform_error.emit("donation_alerts", err)
            )
            self.da_worker.start()
            print("✅ DonationAlerts запущен")
        except Exception as e:
            print(f"❌ DonationAlerts ошибка: {e}")

    def _on_donation_received(self, platform: str, username: str, amount: float, currency: str, message: str):
        print(f"💰 Донат: {username} - {amount} {currency}")
        donate_text = f"💰 {username} задонатил {amount} {currency}"
        if message:
            donate_text += f": {message}"
        self.chat_log.add_chat_message(platform, "DONATION", donate_text, "#FFD700", emotes={}, gifs=[])

    def _load_donation_settings(self):
        from core.settings_manager import SettingsManager
        s = SettingsManager()
        connections = s.settings.get("connections", {})
        da_config = connections.get("donation_alerts", {})
        if da_config.get("enabled") and da_config.get("token"):
            self._connect_donation_alerts(da_config["token"])

    def _check_updates(self):
        try:
            from core.updater import Updater
            self.btn_update.setText("⏳")
            self.btn_update.setEnabled(False)
            self.updater = Updater()
            self.updater.update_available.connect(self._on_update_available)
            self.updater.no_update.connect(self._on_no_update)
            self.updater.error_occurred.connect(self._on_update_error)
            self.updater.update_downloaded.connect(self._on_update_downloaded)
            self.updater_thread = QThread()
            self.updater.moveToThread(self.updater_thread)
            self.updater_thread.started.connect(self.updater.check_for_updates)
            self.updater_thread.start()
        except Exception as e:
            print(f"⚠️ Ошибка обновления: {e}")

    def _on_update_available(self, version: str, url: str):
        reply = QMessageBox.question(self, "Обновление", f"Версия {version}. Скачать?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.updater.download_update(url)

    def _on_no_update(self):
        QMessageBox.information(self, "Chat_AG", "У вас последняя версия!")
        self.btn_update.setText("🔄")
        self.btn_update.setEnabled(True)

    def _on_update_error(self, error: str):
        QMessageBox.critical(self, "Ошибка", f"Не удалось проверить:\n{error}")
        self.btn_update.setText("🔄")
        self.btn_update.setEnabled(True)

    def _on_update_downloaded(self, path: str):
        self.updater.install_update(path)

    def closeEvent(self, event):
        from core.settings_manager import SettingsManager
        from ui.close_dialog import CloseDialog
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