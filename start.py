from core import setup_handler

from aiogram.utils import executor
from dispatcher import dp, bot

from asyncio import create_task, sleep
from aioschedule import run_pending, every

from core.database import database_payment
from time import strftime


async def payment_verification():
    for i in database_payment().get_all_users():
        if i[1] <= strftime("%Y-%m-%d %H:%M:%S"):
            await bot.send_message(
                chat_id = i[0],
                text = 'Платёж истёк!'
            )
            database_payment().delete_payment(
                user_id = i[0]
            )


async def scheduler():
    every(5).seconds.do(payment_verification)

    while True:
        await run_pending()
        await sleep(0.1)


async def on_startup(_):
    create_task(scheduler())


if __name__ == '__main__':
    setup_handler()

    executor.start_polling(
        dispatcher = dp,
        skip_updates = False,
        on_startup = on_startup
    )