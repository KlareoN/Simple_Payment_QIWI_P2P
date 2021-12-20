from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class keyboard_core_init:
    @staticmethod
    async def start(
        pay_url: str
    ) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup()
        keyboard.row_width = 1
        keyboard.add(
            InlineKeyboardButton(
                text = 'Открыть платёж',
                url = pay_url
            ),
            InlineKeyboardButton(
                text = 'Я оплатил',
                callback_data = 'payment_check'
            )
        )
        return keyboard