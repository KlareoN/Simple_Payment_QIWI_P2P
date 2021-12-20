from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from core.database_work.database_payment import database_payment
from core.keyboard.keyboard_core import keyboard_core_init

from config import __TOKEN, __QIWI_P2P_SECRET_KEY, __AMOUNT
from module.qiwi_p2p import QiwiP2P

storage = MemoryStorage()
bot = Bot(
    token = __TOKEN,
    parse_mode = types.ParseMode.HTML
)
dispatcher = Dispatcher(bot, storage=storage)

qiwi_p2p = QiwiP2P(
    secret_key = __QIWI_P2P_SECRET_KEY
)