from dispatcher import dp, types, settings, qiwi_p2p

from core import (
    keyboard_start,
    database_payment
)
from uuid import uuid4

from datetime import datetime, timedelta
from time import strftime


class handler_start:
    @staticmethod
    async def start(
        message: types.Message
    ):
        if not database_payment().exists_payment(
            user_id = message.from_user.id
        ):
            comment = uuid4().__str__()

            bill = qiwi_p2p.create_bill(
                bill_id = uuid4().hex,
                amount = settings().amount,
                comment = comment,
                expiration_datetime = timedelta(minutes = 60)
            )

            database_payment().create_payment(
                user_id = message.from_user.id,
                chat_id = message.chat.id,
                build_id = bill['bill_id'],
                amount = settings().amount,
                comment = comment,
                create_pay = strftime("%Y-%m-%d %H:%M:%S"),
                end_pay = (datetime.now() + timedelta(minutes = 60)).strftime("%Y-%m-%d %H:%M:%S"),
                pay_url = bill['pay_url']
            )

        message_text = (
            f'<b>Привет</>, я выставил тебе счёт через P2P!\n\n'
            f'<b>Сумма платежа:</> <code>{settings().amount:0.2f}₽</>\n'
            f'<i>Время действия платежа ограничено!</>'
        )

        return await message.answer(
            text = message_text,
            reply_markup = await keyboard_start().start(
                pay_url = database_payment().get_payment_information(user_id = message.from_user.id)[6]
            )
        )

    @staticmethod
    async def check_payment(
        call: types.CallbackQuery
    ):
        query = database_payment().get_payment_information(
            user_id = call.from_user.id
        )
        if qiwi_p2p.get_bill(query[0])['status']['value'] == 'PAID':
            database_payment().delete_payment(
                user_id = call.from_user.id
            )

            return await call.answer(
                'Платёж найден!'
            )
        else:
            return await call.answer(
                'Платёж не найден!'
            )


    @staticmethod
    def setup():
        dp.register_message_handler(
            handler_start.start,
            commands = ['start'],
            state = '*',
            chat_type = types.ChatType.PRIVATE
        )

        dp.register_callback_query_handler(
            handler_start.check_payment,
            lambda c: c.data == 'check_payment',
            state = '*',
            chat_type = types.ChatType.PRIVATE
        )
