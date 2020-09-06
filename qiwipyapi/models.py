# https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#payments_model
import uuid


# class Payment:
class Payment:
    """
    Объект, описывающий данные для платежа на провайдера в QIWI Кошельке.
    """

    def __init__(self, value=None, *args, **kwargs):
        self.amount = kwargs.get('amount') or {'value': str(value), 'currency': 'RUB'}
        self.comment = kwargs.get('comment')
        self.expirationDateTime = kwargs.get('expirationDateTime').strftime('%Y-%m-%dT%H:%m:%S+00:00')
        self.customer = kwargs.get('customer')
        self.customFields = kwargs.get('customFields')

    def __repr__(self):
        return self.__dict__

    def __str__(self):
        return str(self.__dict__)

    def to_json(self):
        return self.__dict__


class PaymentInfo:
    """
    Объект, описывающий данные платежной транзакции в QIWI Кошельке. Возвращается в ответ на запросы к платежному API.
    """

    def __init__(self, amount: float = None, **kwargs):
        self.id = kwargs.get('id')
        self.terms = kwargs.get('terms')
        self.fields: dict = kwargs.get('fields')
        self.sum: dict = kwargs.get('sum') or {'amount': amount, 'currency': '643'}
        self.source = 'account_643'
        self.comment: dict = kwargs.get('comment')
        self.transaction: dict = kwargs.get('transaction')
        self.state: dict = kwargs.get('state')


class Transaction:
    pass


class Invoice:
    # x = {'siteId': 'w0drif-00',
    #      'billId': '6ea4405a-ef62-11ea-a84e-4b5ddf829e3f',
    #      'amount': {'currency': 'RUB', 'value': '10.00'},
    #      'status': {'value': 'WAITING', 'changedDateTime': '2020-09-05T13:27:43.141+03:00'},
    #      'creationDateTime': '2020-09-05T13:27:43.141+03:00',
    #      'expirationDateTime': '2020-09-05T17:09:43+03:00',
    #      'payUrl': 'https://oplata.qiwi.com/form/?invoice_uid=76b407cf-aaca-467d-a1cd-545f56383dab'}
    # pass
    # При выставление счёта в ответе приходит payUrl к ссылке можно добавить параметры:
    # https://developer.qiwi.com/ru/p2p-payments/  # option
    # paySource
    # allowedPaySources
    # successUrl
    # lifetime

    def __init__(self, response):
        self.__dict__ = response

    def __repr__(self):
        return self.payUrl
