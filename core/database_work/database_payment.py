from sqlite3 import connect


class database_payment:
    __DB_LOCATION = 'database/payment.db'

    def __init__(self):
        self.__connection = connect(self.__DB_LOCATION)
        self.__cursor = self.__connection.cursor()

    def exists_payment(
        self,
        user_id: int
    ) -> bool:
        """Проверка, есть платёж или нет"""
        self.__cursor.execute(
            'SELECT user_id FROM payment WHERE user_id IN (?)',
            (user_id,)
        )
        if self.__cursor.fetchone() is None:
            return False
        else:
            return True

    def create_payment(
        self,
        user_id: int,
        bill_id: str,
        amount: float,
        comment: str,
        url: str
    ) -> None:
        """Создание платежа"""
        self.__cursor.execute(
            '''
        INSERT INTO payment 
        (user_id, bill_id, amount, comment, url) 
        VALUES (?, ?, ?, ?, ?)
            ''',
            (user_id, bill_id, amount, comment, url, )
        )
        self.__connection.commit()

    def get_information_payment(
        self,
        user_id: int
    ) -> str:
        """Получаем информацию об платеже"""
        self.__cursor.execute(
            '''
        SELECT bill_id, amount, comment, url
        FROM payment WHERE user_id IN (?)
            ''',
            (user_id,)
        )
        return self.__cursor.fetchone()

    def delete_payment(
        self,
        user_id: int
    ) -> None:

        """Удаление платежа"""
        self.__cursor.execute(
            '''
        DELETE FROM payment
        WHERE user_id IN (?) 
            ''',
            (user_id, )
        )
        self.__connection.commit()

    def __enter__(self):
        return self

    def __exit__(self, ext_type, exc_value, traceback):
        self.__cursor.close()

        if isinstance(exc_value, Exception):
            self.__connection.rollback()
        else:
            self.__connection.commit()

        self.__connection.close()

    def __del__(self):
        self.__connection.close()