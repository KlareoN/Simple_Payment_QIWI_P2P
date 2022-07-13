from sqlite3 import connect


class database_payment:
    __slots__ = '__connection'

    def __init__(self):
        self.__connection = connect('database/payment.db')

    def exists_payment(
        self,
        user_id: int | str
    ) -> bool:
        result = self.__connection.execute(
            '''
        SELECT user_id 
        FROM payment 
        WHERE user_id IN (?)
            ''',
            (user_id,)
        ).fetchone()

        if result is None:
            return False
        else:
            return True

    def create_payment(
        self,
        user_id: int | str,
        chat_id: int | str,
        build_id: int | str,
        amount: float,
        comment: str,
        create_pay: str,
        end_pay: str,
        pay_url: str
    ) -> None:
        self.__connection.execute(
            '''
        INSERT INTO payment 
        (user_id, chat_id, build_id, amount, comment, create_pay, end_pay, pay_url) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (user_id, chat_id, build_id, amount, comment, create_pay, end_pay, pay_url, )
        )
        self.__connection.commit()

    def get_payment_information(
        self,
        user_id: int | str
    ) -> list:
        return self.__connection.execute(
            '''
        SELECT chat_id, build_id, amount, comment, create_pay, end_pay, pay_url
        FROM payment 
        WHERE user_id IN (?)
            ''',
            (user_id,)
        ).fetchone()

    def delete_payment(
        self,
        user_id: int | str
    ) -> None:
        self.__connection.execute(
            '''
        DELETE FROM payment
        WHERE user_id IN (?) 
            ''',
            (user_id,)
        )
        self.__connection.commit()

    def get_all_users(self):
        return self.__connection.execute(
            '''
        SELECT chat_id, end_pay
        FROM payment 
            '''
        ).fetchall()

    def __enter__(self):
        return self

    def __exit__(self, ext_type, exc_value, traceback):
        if isinstance(exc_value, Exception):
            self.__connection.rollback()
        else:
            self.__connection.commit()

        self.__connection.close()

    def __del__(self):
        self.__connection.close()