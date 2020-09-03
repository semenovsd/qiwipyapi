# https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#payments_model
import uuid


# class Payment:
class Payment(dict):
    """
    Объект, описывающий данные для платежа на провайдера в QIWI Кошельке.
    """

    def __init__(self, amount: float = None, **kwargs):
        self.id = kwargs.get('id') or str(uuid.uuid1())
        self.sum = kwargs.get('sum') or {'amount': amount, 'currency': '643'}
        self.paymentMethod = kwargs.get('paymentMethod') or {'type': 'Account', 'accountId': '643'}
        self.fields = kwargs.get('fields')
        self.comment = kwargs.get('comment')
        super().__init__()


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
    pass
