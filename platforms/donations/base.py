"""Базовый класс для донат-сервисов"""

from platforms.base import BasePlatformWorker
from PyQt6.QtCore import pyqtSignal


class BaseDonationWorker(BasePlatformWorker):
    """Базовый класс для обработки донатов"""

    donation_received = pyqtSignal(str, str, float, str, str)

    def __init__(self, platform_name: str, config: dict):
        super().__init__(platform_name, config)
        self.token = config.get("token", "")

    def _emit_donation(self, username: str, amount: float, currency: str, message: str):
        """Эмитировать событие получения доната"""
        self.donation_received.emit(
            self.platform_name,
            username,
            amount,
            currency,
            message
        )
        print(f"💰 [{self.platform_name}] Донат: {username} - {amount} {currency} | {message}")