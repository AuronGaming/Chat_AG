"""Воркер для подключения к DonationAlerts"""

import json
from platforms.donations.base import BaseDonationWorker

try:
    import websocket
    WS_AVAILABLE = True
except ImportError:
    WS_AVAILABLE = False
    print("⚠️ Библиотека websocket-client не найдена. Установите: pip install websocket-client")


class DonationAlertsWorker(BaseDonationWorker):
    def __init__(self, config: dict):
        super().__init__("DonationAlerts", config)
        self.ws = None

    def run(self):
        if not WS_AVAILABLE:
            self._emit_error("Не установлен модуль websocket-client")
            return

        if not self.token:
            self._emit_error("Отсутствует токен DonationAlerts")
            return

        self._is_running = True
        self._emit_connected("DonationAlerts")

        ws_url = f"wss://socket.donationalerts.ru:443?token={self.token}"

        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open
        )

        self.ws.run_forever()

    def _on_open(self, ws):
        print("✅ DonationAlerts: WebSocket соединение установлено")

    def _on_close(self, ws, close_status_code, close_msg):
        print(f"⚠️ DonationAlerts: Соединение закрыто (код: {close_status_code})")
        self._emit_disconnected("DonationAlerts")

    def _on_error(self, ws, error):
        print(f"❌ DonationAlerts: Ошибка WebSocket: {error}")
        self._emit_error(str(error))

    def _on_message(self, ws, message):
        try:
            data = json.loads(message)

            if data.get('message_type') == '4':
                payload = json.loads(data['message'])

                username = payload.get('username', 'Аноним')
                amount = float(payload.get('amount', 0))
                currency = payload.get('currency', 'RUB')
                message_text = payload.get('message', '')

                self._emit_donation(username, amount, currency, message_text)

                chat_msg = f"💰 {username} задонатил {amount} {currency}: {message_text}"
                self._emit_message("DonationAlerts", username, chat_msg, "#FFD700")

        except json.JSONDecodeError:
            pass
        except Exception as e:
            print(f"⚠️ Ошибка парсинга сообщения DA: {e}")

    def send_message(self, message: str):
        pass

    def stop(self):
        self._is_running = False
        if self.ws:
            self.ws.close()
        self.quit()
        self.wait(2000)