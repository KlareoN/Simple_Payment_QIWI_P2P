from dispatcher import dispatcher, database_payment, qiwi_p2p, keyboard_core_init, types, __AMOUNT

from datetime import datetime, timedelta


@dispatcher.message_handler(commands=['start'])
async def on_start(
    message: types.Message,
    chat_type = types.ChatType.PRIVATE
):
    user_id_ = message.from_user.id

    if not database_payment().exists_payment(
        user_id = user_id_
    ):
        comment_ = str(hash(f'{datetime.now()}_{user_id_}'))

        expiration_datetime_ = timedelta(
            minutes = 60
        ) # сколько минут будет действовать платёж

        bill = qiwi_p2p.create_bill(
            bill_id = str(datetime.now()),
            amount = __AMOUNT,
            comment = comment_,
            expiration_datetime = expiration_datetime_
        )

        database_payment().create_payment(
            user_id = user_id_,
            bill_id = str(bill['bill_id']),
            amount = __AMOUNT,
            comment = comment_,
            url = bill['pay_url']
        )

    await message.answer(
        text = '👋'
    )
    return await message.answer(
        text = '<b>Привет</b>, я выставил тебе счёт через P2P!\n\n'
               f'<b>Сумма платежа:</b> <code>{__AMOUNT}₽</code>\n'
               f'<i>Время действия платежа ограничено!</i>',

        reply_markup = await keyboard_core_init.start(
            pay_url = database_payment().get_information_payment(
                user_id = user_id_
            )[3]
        )
    )

