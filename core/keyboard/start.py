from dispatcher import types


class keyboard_start:
    @staticmethod
    async def start(
        pay_url: str
    ) -> types.InlineKeyboardMarkup:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row_width = 1
        keyboard.add(
            types.InlineKeyboardButton(
                text = 'Перейти к оплате',
                url = pay_url
            ),
            types.InlineKeyboardButton(
                text = 'Проверить платёж',
                callback_data = 'check_payment'
            )
        )
        return keyboard

