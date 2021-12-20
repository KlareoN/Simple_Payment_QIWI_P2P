from dispatcher import bot, database_payment, qiwi_p2p, types


class callback_query_init:
    @staticmethod
    async def payment_check(call: types.CallbackQuery):
        check_pay = database_payment().get_information_payment(
            user_id = call.message.chat.id
        )

        if qiwi_p2p.get_bill(check_pay[0])['status']['value'] == 'PAID':
            database_payment().delete_payment(
                user_id = call.message.chat.id
            )
            await bot.edit_message_text(
                chat_id = call.message.chat.id,
                message_id = call.message.message_id - 1,
                text = '👍'
            )
            return await bot.edit_message_text(
                chat_id = call.message.chat.id,
                message_id = call.message.message_id,
                text = 'Платёж найден!'
            )

        else:
            return await call.answer(
                text = "Платёж не найден.",
                show_alert = True
            )

