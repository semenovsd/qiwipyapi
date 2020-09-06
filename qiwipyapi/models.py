import time


# https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#payments_model
class Payment:
    """
    Объект, описывающий данные для платежа на провайдера в QIWI Кошельке.
    """

    def __init__(self, amount=None, **kwargs):
        # TODO set to default .get('', default=None)
        self.id = kwargs.get('id') or str(int(time.time() * 1000))  # max 19 len int
        self.sum = kwargs.get('sum') or {'amount': amount, 'currency': '643'}
        self.paymentMethod = {"type": "Account", "accountId": "643"}
        self.fields = kwargs.get('fields')  # Optional
        self.comment = kwargs.get('comment')  # Optional
        self.__dict__.update(kwargs)

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
    def __init__(self, amount=None, **kwargs):
        # TODO set to default .get('', default=None)
        self.id = kwargs.get('id')
        self.terms = kwargs.get('terms')
        self.fields = kwargs.get('fields')
        self.sum = kwargs.get('sum')
        self.source = kwargs.get('source')
        self.comment = kwargs.get('comment')
        self.transaction = kwargs.get('transaction')
        # self.transaction.id = kwargs.get('')
        # self.transaction.state = kwargs.get('')
        self.state = kwargs.get('state')
        # self.state.code = kwargs.get('state')
        self.__dict__.update(kwargs)

    def __repr__(self):
        return self.__dict__

    def __str__(self):
        return str(self.__dict__)

    def to_json(self):
        return self.__dict__


class Transaction:
    pass


# class Invoice:
#     def __init__(self, *args, **kwargs):
#         self.__dict__.update(kwargs)
#     # x = {'siteId': 'w0drif-00',
#     #      'billId': '6ea4405a-ef62-11ea-a84e-4b5ddf829e3f',
#     #      'amount': {'currency': 'RUB', 'value': '10.00'},
#     #      'status': {'value': 'WAITING', 'changedDateTime': '2020-09-05T13:27:43.141+03:00'},
#     #      'creationDateTime': '2020-09-05T13:27:43.141+03:00',
#     #      'expirationDateTime': '2020-09-05T17:09:43+03:00',
#     #      'payUrl': 'https://oplata.qiwi.com/form/?invoice_uid=76b407cf-aaca-467d-a1cd-545f56383dab'}
#     # pass
#     # При выставление счёта в ответе приходит payUrl к ссылке можно добавить параметры:
#     # https://developer.qiwi.com/ru/p2p-payments/  # option
#     # paySource
#     # allowedPaySources
#     # successUrl
#     # lifetime
#
#     def __repr__(self):
#         return self.__dict__.get('payUrl')
#
#     def to_json(self):
#         return self.__dict__


class Balance:
    pass

# response payment_to_card
# p = {'id': '11111111', 'terms': '1963', 'fields': {'account': '4276550078757633'},
#      'sum': {'amount': 10, 'currency': '643'}, 'transaction': {'id': '19741739873', 'state': {'code': 'Accepted'}},
#      'source': 'account_643'}
