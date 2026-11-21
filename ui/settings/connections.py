"""Настройки подключений к платформам"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QLineEdit, QGroupBox, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from ui.theme_config import COLORS
from core.settings_manager import SettingsManager


class ConnectionsSection(QWidget):
    """Секция настроек соединений с кнопками подключения"""

    # Сигналы для связи с главным окном
    connect_requested = pyqtSignal(str, dict)  # (platform_name, config)
    disconnect_requested = pyqtSignal(str)     # platform_name

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {COLORS['bg_main']};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(15, 10, 15, 10)
        lay.setSpacing(12)

        title = QLabel("Соединения")
        title.setStyleSheet(f"font-size: 22px; color: {COLORS['accent']}; font-weight: bold;")
        lay.addWidget(title)

        sub = QLabel("Настройка подключений к стриминговым платформам.")
        sub.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']}; padding-bottom: 10px;")
        lay.addWidget(sub)

        # Загружаем текущие настройки
        s = SettingsManager()
        connections = s.settings.get("connections", {})

        # === Twitch ===
        twitch_cfg = connections.get("twitch", {})
        twitch_group = self._create_group("Twitch")
        twitch_lay = QVBoxLayout(twitch_group)

        twitch_header = QHBoxLayout()
        self.cb_twitch = QCheckBox("Включить Twitch")
        self.cb_twitch.setChecked(twitch_cfg.get("enabled", False))
        self.cb_twitch.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 13px; font-weight: bold;")
        twitch_header.addWidget(self.cb_twitch)
        twitch_header.addStretch()

        self.btn_twitch = QPushButton("🔌 Подключить" if not twitch_cfg.get("enabled") else "🔌 Отключить")
        self.btn_twitch.setFixedSize(130, 30)
        self.btn_twitch.setStyleSheet(self._get_button_style(twitch_cfg.get("enabled", False)))
        self.btn_twitch.clicked.connect(lambda: self._on_connect_click("twitch"))
        twitch_header.addWidget(self.btn_twitch)
        twitch_lay.addLayout(twitch_header)

        twitch_lay.addLayout(self._create_input("Никнейм:", "twitch_nickname", twitch_cfg.get("nickname", "")))
        twitch_lay.addLayout(self._create_input("Токен (OAuth):", "twitch_token", twitch_cfg.get("token", ""), password=True))
        twitch_lay.addLayout(self._create_input("Канал:", "twitch_channel", twitch_cfg.get("channel", "")))
        lay.addWidget(twitch_group)

        # === YouTube ===
        yt_cfg = connections.get("youtube", {})
        yt_group = self._create_group("YouTube")
        yt_lay = QVBoxLayout(yt_group)

        yt_header = QHBoxLayout()
        self.cb_youtube = QCheckBox("Включить YouTube")
        self.cb_youtube.setChecked(yt_cfg.get("enabled", False))
        self.cb_youtube.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 13px; font-weight: bold;")
        yt_header.addWidget(self.cb_youtube)
        yt_header.addStretch()

        self.btn_youtube = QPushButton("🔌 Подключить" if not yt_cfg.get("enabled") else "🔌 Отключить")
        self.btn_youtube.setFixedSize(130, 30)
        self.btn_youtube.setStyleSheet(self._get_button_style(yt_cfg.get("enabled", False)))
        self.btn_youtube.clicked.connect(lambda: self._on_connect_click("youtube"))
        yt_header.addWidget(self.btn_youtube)
        yt_lay.addLayout(yt_header)

        yt_lay.addLayout(self._create_input("API Key:", "youtube_api_key", yt_cfg.get("api_key", ""), password=True))
        yt_lay.addLayout(self._create_input("Channel ID:", "youtube_channel_id", yt_cfg.get("channel_id", "")))
        lay.addWidget(yt_group)

        # === VK Play Live ===
        vk_cfg = connections.get("vk_play", {})
        vk_group = self._create_group("VK Play Live")
        vk_lay = QVBoxLayout(vk_group)

        vk_header = QHBoxLayout()
        self.cb_vk = QCheckBox("Включить VK Play Live")
        self.cb_vk.setChecked(vk_cfg.get("enabled", False))
        self.cb_vk.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 13px; font-weight: bold;")
        vk_header.addWidget(self.cb_vk)
        vk_header.addStretch()

        self.btn_vk = QPushButton("🔌 Подключить" if not vk_cfg.get("enabled") else "🔌 Отключить")
        self.btn_vk.setFixedSize(130, 30)
        self.btn_vk.setStyleSheet(self._get_button_style(vk_cfg.get("enabled", False)))
        self.btn_vk.clicked.connect(lambda: self._on_connect_click("vk_play"))
        vk_header.addWidget(self.btn_vk)
        vk_lay.addLayout(vk_header)

        vk_lay.addLayout(self._create_input("Логин:", "vk_login", vk_cfg.get("login", "")))
        vk_lay.addLayout(self._create_input("Пароль:", "vk_password", vk_cfg.get("password", ""), password=True))
        vk_lay.addLayout(self._create_input("Channel ID:", "vk_channel_id", vk_cfg.get("channel_id", "")))
        lay.addWidget(vk_group)

        # === DonationAlerts ===
        da_cfg = connections.get("donation_alerts", {})
        da_group = self._create_group("DonationAlerts")
        da_lay = QVBoxLayout(da_group)

        da_header = QHBoxLayout()
        self.cb_da = QCheckBox("Включить DonationAlerts")
        self.cb_da.setChecked(da_cfg.get("enabled", False))
        self.cb_da.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 13px; font-weight: bold;")
        da_header.addWidget(self.cb_da)
        da_header.addStretch()

        self.btn_da = QPushButton("🔌 Подключить" if not da_cfg.get("enabled") else "🔌 Отключить")
        self.btn_da.setFixedSize(130, 30)
        self.btn_da.setStyleSheet(self._get_button_style(da_cfg.get("enabled", False)))
        self.btn_da.clicked.connect(lambda: self._on_connect_click("donation_alerts"))
        da_header.addWidget(self.btn_da)
        da_lay.addLayout(da_header)

        da_lay.addLayout(self._create_input("WebSocket Token:", "da_token", da_cfg.get("token", ""), password=True))
        info_label = QLabel("💡 Токен: Настройки DonationAlerts → Виджеты → WebSocket")
        info_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 10px; font-style: italic;")
        da_lay.addWidget(info_label)
        lay.addWidget(da_group)

        lay.addStretch()

    def _get_button_style(self, is_connected: bool) -> str:
        if is_connected:
            return f"""
                QPushButton {{
                    background-color: {COLORS['error']}30;
                    color: {COLORS['error']};
                    border: 1px solid {COLORS['error']};
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['error']}50;
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
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['accent']}50;
                }}
            """

    def _create_group(self, title: str) -> QGroupBox:
        group = QGroupBox(title)
        group.setStyleSheet(f"""
            QGroupBox {{
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-weight: bold;
                border: 1px solid {COLORS['border']};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        return group

    def _create_input(self, label: str, key: str, value: str = "", password: bool = False) -> QHBoxLayout:
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {COLORS['text_primary']}; min-width: 100px; font-size: 12px;")
        row.addWidget(lbl)

        inp = QLineEdit()
        inp.setText(value)
        inp.setPlaceholderText(f"Введите {label.lower()}...")
        inp.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg_input']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['accent']};
            }}
        """)
        if password:
            inp.setEchoMode(QLineEdit.EchoMode.Password)
        inp.setProperty("settings_key", key)
        row.addWidget(inp, stretch=1)
        return row

    def _on_connect_click(self, platform: str):
        """Обработка клика по кнопке подключения"""
        # Сначала сохраняем настройки
        self.save_data()

        s = SettingsManager()
        connections = s.settings.get("connections", {})
        config = connections.get(platform, {})

        if config.get("enabled"):
            # Запрашиваем подключение
            self.connect_requested.emit(platform, config)
        else:
            # Запрашиваем отключение
            self.disconnect_requested.emit(platform)

    def save_data(self):
        s = SettingsManager()
        connections = s.settings.get("connections", {})

        for widget in self.findChildren(QLineEdit):
            key = widget.property("settings_key")
            if key:
                parts = key.split("_", 1)
                if len(parts) == 2:
                    platform, field = parts
                    if platform not in connections:
                        connections[platform] = {}
                    connections[platform][field] = widget.text()

        connections["twitch"]["enabled"] = self.cb_twitch.isChecked()
        connections["youtube"]["enabled"] = self.cb_youtube.isChecked()
        connections["vk_play"]["enabled"] = self.cb_vk.isChecked()
        connections["donation_alerts"]["enabled"] = self.cb_da.isChecked()

        s.settings["connections"] = connections
        s.save()
        print("💾 Настройки соединений сохранены")