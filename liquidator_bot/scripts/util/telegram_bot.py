import telegram
from datetime import datetime


class TelegramBot:
    def __init__(self, chat_id: int, telegram_token: str):
        self._chat_id = chat_id
        self._bot = telegram.Bot(token=telegram_token)

    # todo add levels info, warning, error
    def send(self, tg_msg: str) -> None:
        ts = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        msg = f'[{ts}] {tg_msg}'
        self._bot.sendMessage(chat_id=self._chat_id, text=msg)
