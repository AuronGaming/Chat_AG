"""Twitch OAuth авторизация"""

import webbrowser
from PyQt6.QtCore import QObject, pyqtSignal


class TwitchAuth(QObject):
    """Класс для OAuth авторизации Twitch"""

    token_received = pyqtSignal(str)
    auth_failed = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def open_auth_page(self):
        """Открыть страницу для получения токена"""
        webbrowser.open("https://twitchtokengenerator.com/")
        print("🔑 Twitch: открыт twitchtokengenerator.com")

    def open_twitch_page(self):
        """Открыть сайт Twitch"""
        webbrowser.open("https://www.twitch.tv/")
        print("🔗 Twitch: открыт twitch.tv")

    def start_auth(self):
        """Начать процесс авторизации"""
        self.open_auth_page()
        print("️ Twitch: скопируйте токен и вставьте в настройки")