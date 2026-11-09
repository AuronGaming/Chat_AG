"""Шина событий Chat_AG"""

from PyQt6.QtCore import QObject, pyqtSignal


class EventBus(QObject):
    """Центральная шина событий для связи между модулями"""

    # Сигналы объявлены на уровне класса
    chat_message = pyqtSignal(str, str, str, str, dict, list)
    system_message = pyqtSignal(str, str, str)
    platform_connected = pyqtSignal(str, str)
    platform_disconnected = pyqtSignal(str, str)
    platform_error = pyqtSignal(str, str)
    send_message = pyqtSignal(str, str)
    connect_platform = pyqtSignal(str)
    disconnect_platform = pyqtSignal(str)
    settings_changed = pyqtSignal()
    tts_speak = pyqtSignal(str, str, str)
    tts_mute_changed = pyqtSignal(str, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        print("✅ EventBus создан")