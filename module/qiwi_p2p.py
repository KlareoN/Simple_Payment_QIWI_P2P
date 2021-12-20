# https://github.com/Urmipie/qiwi-p2p-api оригинал.
# я всего лишь это модифицировал :)


import requests

from typing import Optional, Union
from json.decoder import JSONDecodeError
import datetime



def qiwi_format_to_datetime(string: str) -> datetime.datetime:
    """Переводит время, которое присылает Qiwi в datetime UTC"""
    return datetime.datetime.strptime(string.split('.')[0].split('+')[0], '%Y-%m-%dT%H:%M:%S')


class BaseResponse:
    """Базовый класс-дескриптор"""
    def __init__(self, json=None):
        if json is None:
            json = {}
        self.__dict__ = json
        self.json = self.json

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__class__) + ': ' + str(self.__dict__)

    def __getitem__(self, item):
        return self.__dict__[item]

    def __bool__(self):
        return False


class Bill(BaseResponse):
    """
    Класс, возвращаемый вместо JSON с данными счёта. Атрибут .json Содержит исходный dict
    Названия атрибутов совпадают с названиями из документации Qiwi, но "питонизированы"
    (Например, customFields переименован в custom_fields,
    creationDateTime - в creation_datetime, expirationDateTime - в expiration_datetime)
    """
    def __init__(self, json: dict):
        self.site_id: str = json.get('siteId')
        self.bill_id: str = json.get('billId')
        self.amount: dict = json.get('amount', {})
        self.amount_value: Optional[float] = float(self.amount.get('value')) if self.amount.get('value') else None
        self.status: dict = json.get('status', {})
        self.status_value = self.status.get('value')
        self.costumer = json.get('costumer')
        self.custom_fields = json.get('customFields')
        self.comment = json.get('comment')
        self.creation_datetime = qiwi_format_to_datetime(json.get('creationDateTime'))
        self.expiration_datetime = qiwi_format_to_datetime(json.get('expirationDateTime'))
        self.pay_url = json.get('payUrl')
        self.json = json

    def __bool__(self):
        return True


class ErrorResponse(BaseResponse):
    def __init__(self, json: dict, status_code=404):
        self.service_name = json.get('invoicing-api')
        self.error_code = json.get('errorCode')
        self.description = json.get('description')
        self.user_message = json.get('userMessage')
        self.datetime = qiwi_format_to_datetime(json.get('dateTime'))
        self.trace_id = json.get('traceId')
        self.json = json
        self.status_code = status_code

    def __str__(self):
        return str(self.status_code) + ': ' + self.user_message

    def __bool__(self):
        return False


class QiwiP2P:
    def __init__(self, secret_key: str = '', public_key: str = ''):
        """
        Если не указать какой-то из ключей, то при попытке вызвать метод, для которого не указан ключ,
        будет возвращено AssertionError
        """
        self.secret_key = secret_key
        self.public_key = public_key


    def _secret_request(self, method: str, url: str, headers: dict = {}, **kwargs):
        """Запрос с заранее добвленными стандартными хедерами. В остальном - requests.request()"""
        headers['Authorization'] = 'Bearer ' + self.secret_key
        headers['Accept'] = 'application/json'
        response = requests.request(method=method, url=url, headers=headers, **kwargs)
        if response.status_code == 401:
            raise AttributeError('Wrong secret_key: 401 Unauthorized')
        return response

    @staticmethod
    def _get_bill_from_response(response: requests.Response) -> BaseResponse:
        """Переводит response в класс из response_classes"""
        if response.status_code == 200:
            return Bill(json=response.json())
        try:
            json = response.json()
        except JSONDecodeError:
            json = {}
        return ErrorResponse(status_code=response.status_code, json=json)

    def create_bill(self,
                    bill_id: Optional[str] = None,
                    amount: Optional[Union[float, int]] = None,
                    amount_currency: str = 'RUB',
                    phone: str = '',
                    email: str = '',
                    account: str = '',
                    comment: str = '',
                    expiration_datetime: Optional[datetime.timedelta] = None,
                    custom_fields: dict = None,
                    **kwargs) -> Union[str, BaseResponse]:
        """
        Выставление оплаты через форму или по API
        Поля совпадают с таковыми в документации, за исключением "питонофикации": например, billId изменён на bill_id,
        а expirationDateTime - expiration_datetime
        Кроме того, lifetime в выставлении через форму заменено на expiration_datetime

        :param bill_id: Идентификатор выставляемого счета в вашей системе.
                        Он должен быть уникальным и генерироваться на вашей стороне любым способом.
                        Идентификатором может быть любая уникальная последовательность букв или цифр.
                        Также разрешено использование символа подчеркивания (_) и дефиса (-)

        :param amount: Сумма, на которую выставляется счет, округленная в меньшую сторону до 2 десятичных знаков

        :param amount_currency: Валюта для оплаты, дефлотно рубли, указать KZT для тенге
                                Если выдаётся ссылка на форму, тенге недоступны

        :param phone: Номер телефона пользователя (в международном формате)

        :param email: E-mail пользователя

        :param account: Идентификатор пользователя в вашей системе

        :param comment: Комментарий к счету

        :param expiration_datetime: Отрезок времени, по которой счет будет доступен для перевода.
                    Если перевод по счету не будет произведен до этого отрезка,
                    ему присваивается финальный статус EXPIRED и последующий перевод станет невозможен.
                    По истечении 45 суток от даты выставления счет автоматически будет переведен в финальный статус

        :param return_pay_link: Вместо создания формы и возвращения bill вернёт ссылку на оплату и вернёт url если True
                                    (Вместо секретного ключа требуется публичный)
        :param custom_fields: Словарь с пользовательскими данными

        :param success_url: URL для переадресации на ваш сайт в случае успешного перевода (Только в форме!)

        :param kwargs: Именнованные параметры для передачи в requests.request

        :return: Bill, если return_pay_link == False, иначе ссылку на форму оплаты
        """
        if amount:
            amount = f'{float(amount):.2f}'

        if expiration_datetime:
            time = datetime.datetime.utcnow()
            time += expiration_datetime + datetime.timedelta(hours=3)  # перевожу дельту во время и перевожу UTC в МСК
            expiration_datetime = time.strftime('%Y-%m-%dT%H:%M:00+03:00')

        params = {'amount': {'value': amount, 'currency': amount_currency},
                  'customer': {
                                'phone': phone,
                                'email': email,
                                'account': account
                                },
                  'comment': comment,
                  'expirationDateTime': expiration_datetime,
                  'customFields': custom_fields}
        params = dict(filter(lambda item: item[1], params.items()))  # убирает пустые значения

        
        return self._get_bill_from_response(
            self._secret_request(method='PUT', url=f'https://api.qiwi.com/partner/bill/v1/bills/{bill_id}',
                                 headers={'Content-Type': 'application/json'}, json=params, **kwargs)
        )

    def get_bill(self, bill_id, **kwargs) -> BaseResponse:
        """Метод позволяет проверить статус перевода по счету"""
        response = self._secret_request('GET', 'https://api.qiwi.com/partner/bill/v1/bills/' + bill_id, **kwargs)
        return self._get_bill_from_response(response)

    def reject_bill(self, bill_id, **kwargs):
        response = self._secret_request('POST', f'https://api.qiwi.com/partner/bill/v1/bills/{bill_id}/reject',
                                        headers={'Content-Type': 'application/json'}, **kwargs)
        return self._get_bill_from_response(response)
