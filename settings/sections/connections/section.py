"""Главный файл раздела 'Соединения' — вкладки платформ"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget
from ui.theme_config import COLORS
from settings.sections.connections.twitch import TwitchConnectionSection
from settings.sections.connections.youtube import YouTubeConnectionSection
from settings.sections.connections.vk_play import VKConnectionSection


class Section(QWidget):
    """Раздел настроек 'Соединения'"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {COLORS['bg_main']};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(15)

        title = QLabel("Соединения")
        title.setStyleSheet(f"font-size: 22px; color: {COLORS['accent']}; font-weight: bold;")
        lay.addWidget(title)

        sub = QLabel("Подключение к платформам для получения чата и событий.")
        sub.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']}; padding-bottom: 10px;")
        lay.addWidget(sub)

        # Вкладки платформ
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: 1px solid {COLORS['border']}; border-radius: 4px; }}
            QTabBar::tab {{
                background-color: {COLORS['bg_input']};
                color: {COLORS['text_secondary']};
                padding: 8px 16px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['accent']};
                color: white;
            }}
            QTabBar::tab:hover {{
                background-color: {COLORS['bg_hover']};
            }}
        """)

        self.twitch_section = TwitchConnectionSection()
        self.youtube_section = YouTubeConnectionSection()
        self.vk_section = VKConnectionSection()

        self.tabs.addTab(self.twitch_section, "🔴 Twitch")
        self.tabs.addTab(self.youtube_section, "🔴 YouTube")
        self.tabs.addTab(self.vk_section, "🔵 VK Video Live")

        lay.addWidget(self.tabs)

        # Загружаем сохраненные данные при инициализации
        self._load_saved()

    def _load_saved(self):
        """Загрузить сохранённые настройки из файла"""
        from core.settings_manager import SettingsManager
        s = SettingsManager()
        connections = s.settings.get("connections", {})

        if not isinstance(connections, dict):
            connections = {}

        # --- Twitch ---
        twitch = connections.get("twitch", {})
        if hasattr(self.twitch_section, 'enabled_checkbox'):
            self.twitch_section.enabled_checkbox.setChecked(twitch.get('enabled', False))
        if hasattr(self.twitch_section, 'nickname'):
            self.twitch_section.nickname.setText(twitch.get('nickname', ''))
        if hasattr(self.twitch_section, 'url'):
            self.twitch_section.url.setText(twitch.get('site', ''))
        if hasattr(self.twitch_section, 'token'):
            self.twitch_section.token.setText(twitch.get('token', ''))

        # --- YouTube ---
        youtube = connections.get("youtube", {})
        if hasattr(self.youtube_section, 'enabled_checkbox'):
            self.youtube_section.enabled_checkbox.setChecked(youtube.get('enabled', False))
        if hasattr(self.youtube_section, 'channel_url'):
            self.youtube_section.channel_url.setText(youtube.get('channel_id', ''))
        if hasattr(self.youtube_section, 'api_key'):
            self.youtube_section.api_key.setText(youtube.get('api_key', ''))

        # --- VK Video Live (ИСПРАВЛЕНО: загрузка username и session_cookie) ---
        vk = connections.get("vk_play", {})
        if hasattr(self.vk_section, 'enabled_checkbox'):
            self.vk_section.enabled_checkbox.setChecked(vk.get('enabled', False))
        if hasattr(self.vk_section, 'username'):
            self.vk_section.username.setText(vk.get('username', ''))
        if hasattr(self.vk_section, 'session_cookie'):
            self.vk_section.session_cookie.setText(vk.get('session_cookie', ''))

    def save_data(self):
        """Сохранить настройки в файл"""
        from core.settings_manager import SettingsManager
        s = SettingsManager()

        connections = s.settings.get("connections", {})
        if not isinstance(connections, dict):
            connections = {}

        # --- Twitch ---
        connections["twitch"] = {
            'enabled': self.twitch_section.enabled_checkbox.isChecked() if hasattr(self.twitch_section, 'enabled_checkbox') else False,
            'nickname': self.twitch_section.nickname.text() if hasattr(self.twitch_section, 'nickname') else '',
            'site': self.twitch_section.url.text() if hasattr(self.twitch_section, 'url') else '',
            'token': self.twitch_section.token.text() if hasattr(self.twitch_section, 'token') else ''
        }

        # --- YouTube ---
        connections["youtube"] = {
            'enabled': self.youtube_section.enabled_checkbox.isChecked() if hasattr(self.youtube_section, 'enabled_checkbox') else False,
            'channel_id': self.youtube_section.channel_url.text() if hasattr(self.youtube_section, 'channel_url') else '',
            'api_key': self.youtube_section.api_key.text() if hasattr(self.youtube_section, 'api_key') else '',
            'site': self.youtube_section.channel_url.text() if hasattr(self.youtube_section, 'channel_url') else ''
        }

        # --- VK Video Live (ИСПРАВЛЕНО: сохранение username и session_cookie) ---
        connections["vk_play"] = {
            'enabled': self.vk_section.enabled_checkbox.isChecked() if hasattr(self.vk_section, 'enabled_checkbox') else False,
            'username': self.vk_section.username.text() if hasattr(self.vk_section, 'username') else '',
            'session_cookie': self.vk_section.session_cookie.text() if hasattr(self.vk_section, 'session_cookie') else '',
        }

        s.settings["connections"] = connections
        s.save()
        print("💾 Настройки соединений успешно сохранены")