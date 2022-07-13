from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher

from core.dev_functions import QiwiP2P


class settings:
    __slots__ = ('token_qiwi', 'amount', 'token_bot')
    def __init__(self):
        self.token_qiwi = ''
        self.amount = 0
        self.token_bot = ''



bot = Bot(
    token = settings().token_bot,
    parse_mode = types.ParseMode.HTML
)

dp = Dispatcher(
    bot = bot
)

qiwi_p2p = QiwiP2P(
    secret_key = settings().token_qiwi
)