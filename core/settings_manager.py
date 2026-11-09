"""Менеджер настроек Chat_AG"""

import json
import os
from pathlib import Path


class SettingsManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True

        self.settings_dir = Path(os.getenv("APPDATA")) / "Chat_AG"
        self.settings_dir.mkdir(exist_ok=True)
        self.settings_file = self.settings_dir / "settings.json"

        self.defaults = {
            "connections": {
                "twitch": {"enabled": False, "nickname": "", "site": "", "token": ""},
                "youtube": {"enabled": False, "api_key": "", "channel_id": ""},
                "vk_play": {"enabled": False, "login": "", "password": "", "channel_id": ""}
            },
            "tts": {
                "enabled": False,
                "voice_id": "",
                "volume": 100,
                "speed": 0,
                "template": "$text"
            },
            "theme": {
                "accent_color": "#2ea043",
                "font_size": 13
            }
        }

        self.settings = self._load()

    def _load(self) -> dict:
        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                return self._merge(self.defaults, saved)
            except Exception as e:
                print(f"⚠️ Ошибка загрузки настроек: {e}")
        return self._deep_copy(self.defaults)

    def _merge(self, defaults: dict, saved: dict) -> dict:
        result = self._deep_copy(defaults)
        for key, value in saved.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge(result[key], value)
            else:
                result[key] = value
        return result

    def _deep_copy(self, d: dict) -> dict:
        result = {}
        for key, value in d.items():
            if isinstance(value, dict):
                result[key] = self._deep_copy(value)
            else:
                result[key] = value
        return result

    def save(self):
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            print(f"💾 Настройки сохранены: {self.settings_file}")
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")

    def get(self, section: str, key=None, default=None):
        if section not in self.settings:
            return default
        section_data = self.settings[section]
        if key is None:
            return section_data
        if isinstance(section_data, dict):
            return section_data.get(key, default)
        return default

    def set(self, section: str, key: str, value):
        if section not in self.settings:
            self.settings[section] = {}
        if not isinstance(self.settings[section], dict):
            self.settings[section] = {}
        self.settings[section][key] = value
        self.save()