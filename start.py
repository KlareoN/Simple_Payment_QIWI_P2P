from core.handlers import callback_query

from aiogram.utils import executor
from core.core_work import dispatcher

if __name__ == '__main__':
    dispatcher.register_callback_query_handler(
        callback_query.callback_query_init().payment_check, lambda c: c.data == 'payment_check'
    )
    executor.start_polling(
        dispatcher,
        skip_updates = False
    )