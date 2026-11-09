"""Главное окно Chat_AG"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStatusBar, QMessageBox, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QThread, QSize
from ui.theme_config import COLORS
from ui.custom_title_bar import CustomTitleBar
from ui.chat_log import ChatLogWidget
from ui.input_panel import InputPanel
from ui.platform_panel import PlatformPanel
from ui.tray_icon import TrayIcon
from core.event_bus import EventBus
from core.settings_manager import SettingsManager


class MainWindow(QMainWindow):
    """Главное окно приложения"""

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
        self.event_bus = EventBus(self)
        self.active_workers = {}
        self.updater = None
        self.updater_thread = None

        self._init_ui()
        self._connect_signals()
        self._load_and_start_platforms()
        self._init_tts()

    def _init_ui(self):
        central_widget = QWidget()
        central_widget.setStyleSheet(f"background-color: {COLORS['bg_main']};")
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.title_bar = CustomTitleBar("Chat_AG v1.0.3", self)
        main_layout.addWidget(self.title_bar)

        # Кнопка обновления (в заголовке рядом с 🔑)
        from ui.custom_title_bar import create_update_icon
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
            QPushButton:hover {{
                background-color: {COLORS['accent']}30;
            }}
        """)
        self.btn_update.clicked.connect(self._check_updates)
        self.btn_update.setToolTip("Проверить обновления")
        self.title_bar.add_extra_button(self.btn_update)

        self.chat_log = ChatLogWidget()
        main_layout.addWidget(self.chat_log, stretch=1)

        self.input_panel = InputPanel()
        main_layout.addWidget(self.input_panel)

        self.platform_panel = PlatformPanel()
        main_layout.addWidget(self.platform_panel)



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
        self.status_bar.showMessage("Готов к работе. Откройте настройки для подключения.")

        self.chat_log.add_system_message("Twitch", "Ожидание подключения...", "INFO")
        self.chat_log.add_system_message("Система", "Откройте ⚙ Настройки → Соединения для подключения к платформам", "INFO")

        self._init_resize()
        self.tray_icon = TrayIcon(self)

    def _init_resize(self):
        self._resize_handle = QWidget(self)
        self._resize_handle.setFixedSize(20, 20)
        self._resize_handle.setCursor(Qt.CursorShape.SizeFDiagCursor)
        self._resize_handle.setStyleSheet(f"""
            QWidget {{
                background-color: transparent;
                border: none;
            }}
            QWidget:hover {{
                background-color: {COLORS['accent']}40;
                border-radius: 3px;
            }}
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
            tts.template = tts_settings.get('template', '$text')
            print(f"🔊 TTS инициализирован: enabled={tts.enabled}, mute_chat={tts.mute_chat}, mute_donate={tts.mute_donate}")

            # Обновляем состояние кнопок в input_panel
            if hasattr(self.input_panel, 'btn_mute_chat'):
                self.input_panel.btn_mute_chat.setText("🔇 Чат" if tts.mute_chat else "🔊 Чат")
                self.input_panel.btn_mute_chat.setStyleSheet(self._get_sound_button_style(tts.mute_chat))
                self.input_panel.btn_mute_chat.clicked.connect(self._toggle_chat_sound)

            if hasattr(self.input_panel, 'btn_mute_donate'):
                self.input_panel.btn_mute_donate.setText("🔇 Донат" if tts.mute_donate else "🔊 Донат")
                self.input_panel.btn_mute_donate.setStyleSheet(self._get_sound_button_style(tts.mute_donate))
                self.input_panel.btn_mute_donate.clicked.connect(self._toggle_donate_sound)

        except Exception as e:
            print(f"⚠️ Ошибка инициализации TTS: {e}")


    def _load_and_start_platforms(self):
        settings = SettingsManager()
        connections = settings.settings.get("connections", {})
        for platform_name, config in connections.items():
            if isinstance(config, dict) and config.get("enabled", False):
                self._start_platform(platform_name, config)


    def _start_platform(self, platform_name: str, config: dict):
        try:
            module_name = f"platforms.{platform_name}.worker"
            import importlib
            module = importlib.import_module(module_name)
            worker_class = getattr(module, f"{platform_name.title().replace('_', '')}Worker")
            worker = worker_class(platform_name, config)
            worker.connected.connect(lambda ch, p=platform_name: self.event_bus.platform_connected.emit(p, ch))
            worker.disconnected.connect(lambda ch, p=platform_name: self.event_bus.platform_disconnected.emit(p, ch))

            def handle_message(*args, p=platform_name):
                if len(args) == 5:
                    if isinstance(args[0], str) and args[0] in ['vk_play', 'vk', 'youtube', 'twitch']:
                        platform, channel, username, meta, messages = args
                        msg_text = messages[0] if messages else ""
                        color = meta.get("color", "#FFFFFF") if isinstance(meta, dict) else "#FFFFFF"
                        self.event_bus.chat_message.emit(p, username, msg_text, color, {}, [])
                    else:
                        username, message, color, emotes, gifs = args
                        self.event_bus.chat_message.emit(p, username, message, color, emotes or {}, gifs or [])

            worker.message_received.connect(handle_message)
            worker.error_occurred.connect(lambda err, p=platform_name:
                self.event_bus.platform_error.emit(p, err))
            worker.start()
            self.active_workers[platform_name] = worker
            self.chat_log.add_system_message(platform_name, f"Запуск {platform_name}...", "INFO")
        except ImportError:
            self.chat_log.add_system_message(platform_name, f"Модуль {platform_name} не найден", "ERROR")
        except Exception as e:
            self.chat_log.add_system_message(platform_name, f"Ошибка запуска: {e}", "ERROR")

    def _stop_platform(self, platform_name: str):
        if platform_name in self.active_workers:
            worker = self.active_workers[platform_name]
            worker.stop()
            del self.active_workers[platform_name]
            self.chat_log.add_system_message(platform_name, "Остановлен", "WARNING")

    def _on_send_message(self, message: str):
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
        self.chat_log.add_chat_message(platform, username, message, color, emotes=emotes, gifs=gifs)

        platform_code = platform.upper()[:2]
        self.platform_panel.increment_counter(platform_code)

        # Озвучка (если не замьючено)
        try:
            from tts.manager import TTSManager
            tts = TTSManager()
            if tts.enabled and not tts.mute_chat:
                tts_text = f"{username}: {message}"
                tts.speak(tts_text, is_donate=False)
        except Exception as e:
            print(f"⚠️ Ошибка TTS: {e}")

    def _on_system_message(self, platform: str, message: str, level: str):
        self.chat_log.add_system_message(platform, message, level)

    def _on_platform_connected(self, platform: str, channel: str):
        self.chat_log.add_system_message(platform, f"Подключено к {channel}", "SUCCESS")
        self.platform_panel.set_platform_active(platform.upper()[:2], True)
        self.status_bar.showMessage(f"Подключено: {platform}")

    def _on_platform_disconnected(self, platform: str, channel: str):
        self.chat_log.add_system_message(platform, f"Отключено от {channel}", "WARNING")
        self.platform_panel.set_platform_active(platform.upper()[:2], False)

    def _on_platform_error(self, platform: str, error: str):
        self.chat_log.add_system_message(platform, error, "ERROR")

    def open_settings(self):
        if not self.settings_window:
            from settings.settings_window import SettingsWindow
            self.settings_window = SettingsWindow()
            self.settings_window.settings_applied.connect(self._on_settings_applied)
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def open_activation(self):
        print("🔑 Открытие окна активации...")

    def _on_settings_applied(self):
        self.chat_log.add_system_message("Система", "Настройки применены, перезапуск платформ...", "INFO")
        self.platform_panel.reset_counters()
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
            tts.template = tts_settings.get('template', '$text')
            print(f"🔊 TTS обновлён: enabled={tts.enabled}, mute_chat={tts.mute_chat}, mute_donate={tts.mute_donate}")

            if hasattr(self, 'btn_mute_chat'):
                self.btn_mute_chat.setText("🔇 Чат" if tts.mute_chat else "🔊 Чат")
                self.btn_mute_chat.setStyleSheet(self._get_sound_button_style(tts.mute_chat))
            if hasattr(self, 'btn_mute_donate'):
                self.btn_mute_donate.setText("🔇 Донат" if tts.mute_donate else "🔊 Донат")
                self.btn_mute_donate.setStyleSheet(self._get_sound_button_style(tts.mute_donate))
        except Exception as e:
            print(f"⚠️ Ошибка обновления TTS: {e}")
        for platform_name in list(self.active_workers.keys()):
            self._stop_platform(platform_name)
        self._load_and_start_platforms()

    # ===== МЕТОДЫ ОБНОВЛЕНИЯ =====

    def _check_updates(self):
        try:
            from core.updater import Updater
            self.btn_update.setText("⏳ Проверка...")
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
            print(f"⚠️ Ошибка проверки обновлений: {e}")
            self.btn_update.setText("🔄 Обновить")
            self.btn_update.setEnabled(True)

    def _on_update_available(self, version: str, url: str):
        reply = QMessageBox.question(
            self,
            "Доступно обновление",
            f"Найдена версия {version}.\nСкачать и установить?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.btn_update.setText("⬇️ Скачивание...")
            self.updater.download_update(url)
        else:
            self.btn_update.setText("🔄 Обновить")
            self.btn_update.setEnabled(True)

    def _on_no_update(self):
        QMessageBox.information(self, "Chat_AG", "У вас последняя версия!")
        self.btn_update.setText("🔄 Обновить")
        self.btn_update.setEnabled(True)

    def _on_update_error(self, error: str):
        QMessageBox.critical(self, "Ошибка", f"Не удалось проверить обновления:\n{error}")
        self.btn_update.setText("🔄 Обновить")
        self.btn_update.setEnabled(True)

    def _on_update_downloaded(self, path: str):
        self.updater.install_update(path)

    def _get_sound_button_style(self, muted: bool) -> str:
        if muted:
            return f"""
                QPushButton {{
                    background-color: {COLORS['bg_input']};
                    color: {COLORS['text_secondary']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 4px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['bg_hover']};
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: {COLORS['accent']}30;
                    color: {COLORS['accent']};
                    border: 1px solid {COLORS['accent']};
                    border-radius: 4px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['accent']}50;
                }}
            """

    def _toggle_chat_sound(self):
        from tts.manager import TTSManager
        tts = TTSManager()
        tts.mute_chat = not tts.mute_chat
        if hasattr(self.input_panel, 'btn_mute_chat'):
            self.input_panel.btn_mute_chat.setText("🔇 Чат" if tts.mute_chat else "🔊 Чат")
            self.input_panel.btn_mute_chat.setStyleSheet(self._get_sound_button_style(tts.mute_chat))
        self._save_tts_settings()

    def _toggle_donate_sound(self):
        from tts.manager import TTSManager
        tts = TTSManager()
        tts.mute_donate = not tts.mute_donate
        if hasattr(self.input_panel, 'btn_mute_donate'):
            self.input_panel.btn_mute_donate.setText("🔇 Донат" if tts.mute_donate else "🔊 Донат")
            self.input_panel.btn_mute_donate.setStyleSheet(self._get_sound_button_style(tts.mute_donate))
        self._save_tts_settings()

    def _save_tts_settings(self):
        from tts.manager import TTSManager
        from core.settings_manager import SettingsManager
        tts = TTSManager()
        s = SettingsManager()
        tts_settings = s.settings.get("tts", {})
        tts_settings["mute_chat"] = tts.mute_chat
        tts_settings["mute_donate"] = tts.mute_donate
        s.settings["tts"] = tts_settings
        s.save_settings()

    def closeEvent(self, event):
        from core.settings_manager import SettingsManager
        s = SettingsManager()
        saved_action = s.settings.get("close_action", "ask")

        if saved_action == "minimize":
            print("💾 Сохраненный выбор: свернуть в трей")
            event.ignore()
            self.hide()
            if hasattr(self, 'tray_icon') and self.tray_icon:
                self.tray_icon.show()
            return
        elif saved_action == "exit":
            print("💾 Сохраненный выбор: закрыть полностью")
            event.accept()
            return

        print("❓ Показываю диалог закрытия...")
        from ui.close_dialog import CloseDialog
        dialog = CloseDialog(self)

        if dialog.exec():
            choice = dialog.get_choice()
            if choice == "minimize":
                print("📥 Сворачиваю в трей...")
                event.ignore()
                self.hide()
                if hasattr(self, 'tray_icon') and self.tray_icon:
                    self.tray_icon.show()
            else:
                print("🔴 Закрываю полностью...")
                event.accept()
        else:
            print("❌ Отмена закрытия")
            event.ignore()