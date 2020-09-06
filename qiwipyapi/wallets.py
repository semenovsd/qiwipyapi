#!/usr/bin/env python
# -*- coding: utf-8 -*-


import uuid

from .request import request
from .response import response

from .errors import payment_history_exception, PaymentHistoryError
from .models import Payment, PaymentInfo

from datetime import datetime, timedelta
from dateutil.tz import tzlocal


class BaseWallet:
    """ Родительский класс для работы с QIWI Wallet API и QIWI P2P API.
    Определяёт __init__ и общие методы кошельков.

    """

    def __init__(self, wallet_number, token):
        self._WALLET_NUMBER = wallet_number
        self._TOKEN = token
        self._HEADERS = {'Accept': 'application/json',
                         'Content-Type': 'application/json',
                         'Authorization': f'Bearer {self._TOKEN}'}

    def _request(self, method, request_url, **kwargs):
        return response(request(method, request_url, **kwargs))

    def _payment(self, *args, **kwargs):
        return Payment(*args, **kwargs).to_json()

    def _payment_info(self, *args, **kwargs):
        return PaymentInfo(*args, **kwargs)


class P2PWallet(BaseWallet):
    """ Класс для работы с QIWI P2P API.
    Поддерживает все методы и параметры api:
    https://developer.qiwi.com/ru/p2p-payments

    :param _WALLET_NUMBER: Qiwi wallet number in format 79219876543 without +
    :param _P2P_SEC_KEY: Ключи создаются в личном кабинете в разделе "API" (на сайте p2p.qiwi.com)
    :return: New wallet
    """

    def create_invoice(self, value, bill_id=None,
                       expirationDateTime=None, **kwargs):
        """ Выставить новый счёт
        https://developer.qiwi.com/ru/p2p-payments/#create

        :param value: данные о сумме счета
        :param bill_id: уникальный идентификатор счета в вашей системе
        :param expirationDateTime:
        :param kwargs: дополнительные параметры
        :return: ??? подумать, что именно возвращать (урл или весь ответ) или вообще отдавать объект
        """
        method = 'put'
        request_url = f'https://api.qiwi.com/partner/bill/v1/bills/{bill_id if bill_id else uuid.uuid1()}'
        json_data = dict()
        json_data['amount'] = {'value': value, 'currency': 'RUB'}
        if expirationDateTime is None:
            expirationDateTime = datetime.now(tz=tzlocal()) + timedelta(hours=1)
            json_data['expirationDateTime'] = expirationDateTime.strftime('%Y-%m-%dT%H:%m:%S+00:00')
        json_data.update(kwargs)
        return self._request(method, request_url, headers=self._HEADERS, json=json_data)

    def invoice_status(self, bill_id):
        """ Проверка счёта
        https://developer.qiwi.com/ru/p2p-payments/#invoice-status

        :param bill_id: уникальный идентификатор счета в вашей системе.
        :return:
        :raises:
            RequestException: если счёта нет
        """
        method = 'get'
        request_url = f'https://api.qiwi.com/partner/bill/v1/bills/{bill_id}'
        return self._request(method, request_url, headers=self._HEADERS)

    def cancel_invoice(self, bill_id):
        """ Отмена счёта
        https://developer.qiwi.com/ru/p2p-payments/#cancel

        :param bill_id: уникальный идентификатор счета в вашей системе.
        :return:
        """
        method = 'post'
        request_url = f'https://api.qiwi.com/partner/bill/v1/bills/{bill_id}/reject'
        return self._request(method, request_url, headers=self._HEADERS)


class QIWIWallet(BaseWallet):
    """ Класс для работы с QIWI Wallet API.
    Поддерживает все методы и параметры api:
    https://qiwi.com/api

    :param _WALLET_NUMBER: Qiwi wallet number in format 79219876543 without +
    :param _WALLET_TOKEN: Qiwi wallet token
    :param _P2P_SEC_KEY: Ключи создаются в личном кабинете в разделе "API" (на сайте p2p.qiwi.com)
    :return: New wallet
    """

    def wallet_profile(self, authInfoEnabled: bool = True, contractInfoEnabled: bool = True,
                       userInfoEnabled: bool = True):
        """ Метод возвращает информацию о вашем профиле - наборе пользовательских данных и настроек вашего QIWI кошелька.
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#profile

        :param authInfoEnabled: логический признак выгрузки настроек авторизации.
        :param contractInfoEnabled: логический признак выгрузки данных о вашем QIWI кошельке.
        :param userInfoEnabled: логический признак выгрузки прочих пользовательских данных.
        :return:
        """
        method = 'get'
        request_url = f'https://edge.qiwi.com/person-profile/v1/profile/current'
        params = f'authInfoEnabled={authInfoEnabled}&' \
                 f'contractInfoEnabled={contractInfoEnabled}&' \
                 f'userInfoEnabled={userInfoEnabled}'
        return self._request(method, request_url, headers=self._HEADERS, params=params)

    def ident(self, birthDate: str, firstName: str, middleName: str, lastName: str, passport: str, inn: str = None,
              snils: str = None, oms: str = None) -> dict:
        """ Данный метод позволяет отправить данные для идентификации вашего QIWI кошелька.
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#ident

        :param birthDate: Дата рождения пользователя (в формате "ГГГГ-ММ-ДД")
        :param firstName: Имя пользователя
        :param middleName: Отчество пользователя
        :param lastName: Фамилия пользователя
        :param passport: Серия и номер паспорта пользователя (только цифры) xxxx xxxxxx
        :param inn: ИНН пользователя
        :param snils: Номер СНИЛС пользователя
        :param oms: Номер полиса ОМС пользователя
        :return:
        :exception:
            AssertionError: Если не указан один из параметров: ИНН, СНИЛС, ОМС
        """
        try:
            assert inn or snils or oms
        except AssertionError:
            raise AssertionError('Укажите минимум один из параметров: ИНН, СНИЛС, ОМС')
        method = 'post'
        request_url = f'https://edge.qiwi.com/identification/v1/persons/{self._WALLET_NUMBER}/identification'
        json_data = dict()
        json_data['birthDate'] = birthDate
        json_data['firstName'] = firstName
        json_data['middleName'] = middleName
        json_data['lastName'] = lastName
        json_data['passport'] = passport
        json_data['inn'] = inn
        json_data['snils'] = snils
        json_data['oms'] = oms
        return self._request(method, request_url, headers=self._HEADERS, json=json_data)

    def ident_data(self) -> dict:
        """ Данный метод позволяет выгрузить маскированные данные и статус идентификации своего QIWI кошелька.
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#ident_data

        :return:
        """
        method = 'get'
        request_url = f'https://edge.qiwi.com/identification/v1/persons/{self._WALLET_NUMBER}/identification'
        return self._request(method, request_url, headers=self._HEADERS)

    def limits(self, types: list) -> dict:
        """ Метод возвращает текущие уровни лимитов по операциям в вашем QIWI кошельке.
        Лимиты действуют как ограничения на сумму определенных операций.
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#limits

        :param types: list of:
            EFILL - максимальный допустимый остаток на счёте
            TURNOVER - оборот в месяц
            PAYMENTS_P2P - переводы на другие кошельки в месяц
            PAYMENTS_PROVIDER_INTERNATIONALS - платежи в адрес иностранных компаний в месяц
            PAYMENTS_PROVIDER_PAYOUT - Переводы на банковские счета и карты, кошельки других систем
            WITHDRAW_CASH - снятие наличных в месяц. Должен быть указан хотя бы один тип операций.
        :return:
        :exception:
            AssertionError: Если не указан один из параметров: ИНН, СНИЛС, ОМС
        """
        try:
            assert types
        except AssertionError:
            raise AssertionError('Задайте список типов операций, по которым запрашиваются лимиты.')
        method = 'get'
        request_url = f'https://edge.qiwi.com/qw-limits/v1/persons/{self._WALLET_NUMBER}/actual-limits'
        params = {}
        for i, operation in enumerate(types):
            params['types[' + str(i) + ']'] = operation
        return self._request(method, request_url, headers=self._HEADERS, params=params)

    def restrictions(self) -> dict:
        """ Проверка ограничений исходящих платежей с QIWI Кошелька
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#restrictions

        :return:
        """
        method = 'get'
        request_url = f'https://edge.qiwi.com/person-profile/v1/persons/{self._WALLET_NUMBER}/status/restrictions'
        return self._request(method, request_url, headers=self._HEADERS)

    def payments_history(self, rows: int = 10, operation='ALL', sources=None) -> list:
        """ История платежей
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#payments_history

        :param rows:
        :param operation:
        :param sources:
        :return:
        """
        method = 'get'
        request_url = f'https://edge.qiwi.com/payment-history/v2/persons/{self._WALLET_NUMBER}/payments'
        params = dict()
        params['rows'] = rows
        params['operation'] = operation
        params['sources'] = sources
        # TODO кидать ошибку, если платежей нет и всё что с этим связанно
        # Ошибки перечислены в параметре errorCode ответа
        # Возможно имеет смысл сделать отдельную ошибку и выводить код ошибки и описание
        # Или делать на каждую ошибку своё исключение
        # https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#search
        r = self._request(method, request_url, headers=self._HEADERS, params=params).get('data')
        # TODO обрабатывать здесь или в response()
        if r == '':  # ответ получен без ошибки, но данные пусты
            e = payment_history_exception(r)
            raise PaymentHistoryError(e)
        return r

    def payment_stat(self, start_date: datetime, end_date: datetime, operation: str = 'ALL', source: list = None):
        """ Статистика платежей
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#stat

        Дату можно указать в любой временной зоне TZD (формат ГГГГ-ММ-ДД'T'чч:мм:ссTZD),
        однако она должна совпадать с временной зоной в параметре endDate.
        Обозначение временной зоны TZD: +чч:мм или -чч:мм (временной сдвиг от GMT).

        :param start_date: Начальная дата периода статистики. Обязательный параметр.
        :param end_date: Конечная дата периода статистики. Обязательный параметр.
        :param operation: Тип операций, учитываемых при подсчете статистики.
        :param source: Источники платежа, по которым вернутся данные.
        :return:
        """
        method = 'get'
        request_url = f'https://edge.qiwi.com/payment-history/v2/persons/{self._WALLET_NUMBER}/payments/total'
        params = dict()
        params['startDate'] = start_date
        params['endDate'] = end_date
        params['operation'] = operation
        params['source'] = source
        return self._request(method, request_url, headers=self._HEADERS, params=params)

    def transactions_info(self, transaction_id, type: str = None):
        """ Информация о транзакции
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#txn_info

        :param transaction_id: номер транзакции из истории платежей (параметр data[].txnId в ответе).
        :param type: тип транзакции из истории платежей (параметр data[].type в ответе). Optional.
        :return:
        """
        method = 'get'
        request_url = f'https://edge.qiwi.com/payment-history/v2/transactions/{transaction_id}?type={type}'
        # TODO if not transaction raise error
        return self._request(method, request_url, headers=self._HEADERS)['Transaction']

    def cheque_file(self, transaction_id, type: str = None, format: str = 'PDF'):
        """ Данный метод используется для получения электронной квитанции (чека) по определенной транзакции
        из вашей истории платежей в формате PDF/JPEG в виде файла
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#payment_receipt

        :param transaction_id: номер транзакции из истории платежей (параметр data[].txnId в ответе).
        :param type: тип транзакции из истории платежей (параметр data[].type в ответе).
        :param format: тип файла, в который сохраняется квитанция. Допустимые значения: JPEG, PDF
        :return: Успешный ответ содержит файл выбранного формата в бинарном виде.
        """
        method = 'get'
        request_url = f'https://edge.qiwi.com/payment-history/v1/transactions/{transaction_id}/cheque/file?' \
                      f'type={type}&format={format}'
        # response in binary format
        return self._request(method, request_url, headers=self._HEADERS)

    def cheque_to_email(self, transaction_id, type: str, email: str):
        """ Данный метод используется для получения электронной квитанции (чека) по определенной транзакции
        из вашей истории платежей в формате PDF/JPEG в виде файла почтовым сообщением на заданный e-mail.
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#payment_receipt

        :param transaction_id: номер транзакции из истории платежей (параметр data[].txnId в ответе).
        :param type: тип транзакции из истории платежей (параметр data[].type в ответе).
        :param email: Адрес для отправки электронной квитанции.
        :return: Успешный ответ содержит HTTP-код результата операции отправки файла.
        """
        method = 'post'
        request_url = f'https://edge.qiwi.com/payment-history/v1/transactions/{transaction_id}/cheque/send'
        json_data = dict()
        json_data['type'] = type
        json_data['email'] = email
        return self._request(method, request_url, headers=self._HEADERS, json=json_data)

    def list_balances(self) -> dict:
        """ Список балансов
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#balances_list

        :return: Ответ содержит массив счетов вашего QIWI Кошелька для фондирования платежей и текущие балансы счетов.
        """
        method = 'get'
        request_url = f'https://edge.qiwi.com/funding-sources/v2/persons/{self._WALLET_NUMBER}/accounts'
        # TODO сделать отдельный класс балансы
        return self._request(method, request_url, headers=self._HEADERS)

    def create_balance(self, alias: str):
        """ Создание баланса. Метод создает новый счет и баланс в вашем QIWI Кошельке.
        Список доступных для создания счетов можно получить с помощью метода funding_offer.
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#balance_create

        :param alias: Псевдоним нового счета (см. запрос доступных счетов)
        :return: Успешный ответ содержит HTTP-код 201.
        """
        method = 'post'
        request_url = f'https://edge.qiwi.com/funding-sources/v2/persons/{self._WALLET_NUMBER}/accounts'
        json_data = {'alias': alias}
        return self._request(method, request_url, headers=self._HEADERS, json=json_data)

    def funding_offer(self) -> object:
        """ Запрос доступных счетов. Метод отображает псевдонимы счетов, доступных для создания в вашем QIWI Кошельке.
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#funding_offer

        :return: Успешный твет содержит данные о счетах, которые можно создать.
        """
        method = 'get'
        request_url = f'https://edge.qiwi.com/funding-sources/v2/persons/{self._WALLET_NUMBER}/accounts/offer'
        return self._request(method, request_url, headers=self._HEADERS)

    def default_account(self, account_alias: str, default: bool = True):
        """ Установка баланса по умолчанию.
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#default_balance

        :param account_alias: Псевдоним счета в кошельке из списка счетов (параметр accounts[].alias в ответе).
        :param default: Признак установки счета по умолчанию.
        :return: Успешный ответ содержит HTTP-код 204.
        """
        method = 'patch'
        request_url = f'https://edge.qiwi.com/funding-sources/v2/persons/{self._WALLET_NUMBER}/accounts/{account_alias}'
        json_data = {'defaultAccount': default}
        # TODO change response to bool ?
        return self._request(method, request_url, headers=self._HEADERS, json=json_data)

    def get_commission(self, id: str, amount: float, account: str = None, **kwargs):
        """ Узнать комиссию. Метод для получения комиссии за платеж до его совершения.
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#rates

        :param id: Идентификатор провайдера.
        :param amount:
        :param account:
        :param kwargs:
        :return: Возвращается полная комиссия QIWI Кошелька за платеж в пользу указанного провайдера
        с учетом всех тарифов по заданному набору платежных реквизитов.
        """
        method = 'post'
        request_url = f'https://edge.qiwi.com/sinap/providers/{id}/onlineCommission'
        json_data = dict()
        json_data['account'] = account or self._WALLET_NUMBER
        json_data['paymentMethod'] = dict()
        json_data['paymentMethod']['type'] = 'Account'
        json_data['paymentMethod']['accountId'] = '643'
        json_data['purchaseTotals'] = dict()
        json_data['purchaseTotals']['total'] = dict()
        json_data['purchaseTotals']['total']['amount'] = float(amount)
        json_data['purchaseTotals']['total']['currency'] = '643'
        json_data.update(kwargs)
        return self._request(method, request_url, headers=self._HEADERS, json=json_data)['qwCommission']['amount']

    def autocomplete_form(self, id: int, amountInteger: int = None, amountFraction: int = None, comment: str = None,
                          account: str = None, blocked: list = None, accountType: str = None):
        # TODO выбрать что возвращает данный метод, ссылку с гет параметрами или ссылку на сформированную страницу.
        """ Предзаполненная форма платежа. Данный метод отображает в браузере предзаполненную форму на сайте qiwi.com
        для совершения платежа.
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#autocomplete

        :param id: Идентификатор провайдера.
        :param amountInteger: Целая часть суммы платежа (рубли).
        Если параметр не указан, поле "Сумма" на форме будет пустым.
        Допустимо число не больше 99 999 (ограничение на сумму платежа)
        :param amountFraction: Дробная часть суммы платежа (копейки).
        Если параметр не указан, поле "Сумма" на форме будет пустым.
        :param comment: Комментарий. Параметр используется только для ID=99.
        :param account: Код провайдера. См. документацию.
        :param blocked: Список неизменяемых полей. См. документацию.
        :param accountType: Параметр используется только для ID=99999.
        Значение определяет перевод на QIWI кошелек по никнейму или по номеру кошелька.
        :return: ???
        """
        method = 'get'
        request_url = f'https://qiwi.com/{id}'
        params = dict()
        params['amountInteger'] = amountInteger
        params['amountFraction'] = amountFraction
        params['currency'] = '643'
        params['extra'] = dict()
        params['extra']['comment'] = comment if id == 99 else None
        params['extra']['account'] = account
        params['extra']['accountType'] = accountType if id == 99999 else None
        params['blocked'] = blocked
        # TODO выбрать, что возвращать
        return self._request(method, request_url, headers=self._HEADERS, params=params)

    def nickname(self):
        """ Узнать свой никнейм через API.
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#autocomplete

        :return:
        """
        method = 'get'
        request_url = f'https://edge.qiwi.com/qw-nicknames/v1/persons/{self._WALLET_NUMBER}/nickname'
        return self._request(method, request_url, headers=self._HEADERS)['nickname']

    def payment_to_wallet(self, amount: float, pay_to: str):
        """ Перевод на киви кошелёк.
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#p2p

        :param amount: Сумма перевода.
        :param pay_to: Номер кошелька для перевода.
        :return:
        """
        method = 'post'
        request_url = f'https://edge.qiwi.com/sinap/api/v2/terms/99/payments'
        fields = {'fields': {'account': pay_to}}
        payment = Payment(amount=amount, fields=fields)
        r = self._request(method, request_url, headers=self._HEADERS, json=payment)
        # TODO test
        payment_info = PaymentInfo(r['PaymentInfo'])
        return payment_info

    def exchange(self, amount: float, currency: str, pay_to: str):
        """ Конвертировать средства.
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#CCY

        :param amount: Сумма для конвертации.
        :param currency: Код валюты. Допускается '398', '840', '978'.
        :param pay_to: Номер кошелька для перевода.
        :return:
        """
        method = 'post'
        request_url = f'https://edge.qiwi.com/sinap/api/v2/terms/1099/payments'
        currencies = ['398', '840', '978']
        if currency not in currencies:
            print('This currency not available')
            return
        sum = {'amount': amount, 'currency': currency}
        fields = {'account': pay_to}
        payment = Payment(sum=sum, fields=fields)
        r = self._request(method, request_url, headers=self._HEADERS, json=payment)
        # TODO test
        payment_info = PaymentInfo(r['PaymentInfo'])
        return payment_info

    def cross_rates(self):
        """  Курсы валют. Метод возвращает текущие курсы и кросс-курсы валют КИВИ Банка.
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#exchange

        :return:
        """
        method = 'get'
        request_url = f'https://edge.qiwi.com/sinap/crossRates'
        # TODO return currency pair if request in method
        return self._request(method, request_url, headers=self._HEADERS)['result']

    def pay_mobile(self, id: str, to_mobile: str):
        """ Оплата сотовой связи.
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#cell

        :param id: Идентификатор провайдера. Определяется с помощью метода проверки мобильного оператора.
        :param to_mobile: Номер мобильного телефона для пополнения (без префикса 8).
        :return: PaymentInfo
        """
        method = 'post'
        request_url = f'https://edge.qiwi.com/sinap/api/v2/terms/{id}/payments'
        fields = {'account': to_mobile}
        payment = Payment(fields=fields)  # TODO sum ???
        r = self._request(method, request_url, headers=self._HEADERS, json=payment)
        # TODO test
        payment_info = PaymentInfo(r['PaymentInfo'])
        return payment_info

    def payment_to_card(self, amount, card_number: str, provider_id: str, **kwargs):
        """ Перевод на карту. Метод выполняет денежный перевод на карты платежных систем Visa, MasterCard или МИР.
        Код провайдера можно узнать методом search_provider_for_card.
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#cards

        :param amount:
        :param card_number:
        :param provider_id:
        :param kwargs:
        :return: PaymentInfo
        """
        method = 'post'
        request_url = f'https://edge.qiwi.com/sinap/api/v2/terms/{provider_id}/payments'
        fields = {'account': card_number}
        json_data = self._payment(amount=amount, fields=fields, *kwargs)
        print(json_data)
        # TODO кидать ошибку, если не хватает денег и всё что не связанно с корректностью данных
        r = self._request(method, request_url, headers=self._HEADERS, json=json_data)
        print(self._payment_info(r))
        return r

    def transfer_to_card(self, provider_id: str, account: str, account_type: str, mfo: str, lname: str,
                         fname: str, mname: str, exp_date: str = None):
        """ Перевод по номеру карты. Метод выполняет денежный перевод на карты физических лиц, выпущенные российскими банками.
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#banks

        :param provider_id: Идентификатор провайдера.
        :param account: Номер банковской карты получателя (без пробелов).
        :param exp_date: Срок действия карты, в формате ММГГ (например, 0218).
        :param account_type: Тип банковского идентификатора. См. Документацию.
        :param mfo: БИК соответствующего банка/территориального отделения банка.
        :param lname: Фамилия получателя.
        :param fname: Имя получателя.
        :param mname: Отчество получателя.
        :return: PaymentInfo
        """
        method = 'post'
        request_url = f'https://edge.qiwi.com/sinap/api/v2/terms/{provider_id}/payments'
        fields = dict()
        fields['account'] = account
        fields['exp_date'] = exp_date if id in ['464', '821'] else None
        fields['account_type'] = account_type
        fields['mfo'] = mfo
        fields['lname'] = lname
        fields['fname'] = fname
        fields['mname'] = mname
        payment = Payment(fields=fields)  # TODO sum ???
        r = self._request(method, request_url, headers=self._HEADERS, json=payment)
        # TODO test
        payment_info = PaymentInfo(r['PaymentInfo'])
        return payment_info

    def transfer_to_account(self, provider_id: str, account: str, urgent: str, mfo: str, account_type: str, lname: str,
                            fname: str, mname: str, agrnum: str = None):
        """ Перевод по номеру счета/договора. Метод выполняет денежный перевод на счета физических лиц,
        открытые в российских банках. Возможен обычный перевод или перевод с использованием сервиса срочного перевода
        (исполнение в течение часа, с 9:00 до 19:30).
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#banks

        :param provider_id: Идентификатор провайдера.
        :param account: Номер банковского счета получателя
        :param urgent: Признак ускоренного перевода.
        :param mfo: БИК соответствующего банка/территориального отделения банка
        :param account_type: Тип банковского идентификатора.
        :param lname: Фамилия получателя
        :param fname: Имя получателя
        :param mname: Отчество получателя
        :param agrnum: Номер договора - для переводов в ХоумКредит Банк
        :return:
        """
        method = 'post'
        request_url = f'https://edge.qiwi.com/sinap/api/v2/terms/{provider_id}/payments'
        fields = dict()
        fields['account'] = account
        fields['urgent'] = urgent
        fields['mfo'] = mfo
        fields['account_type'] = account_type
        fields['lname'] = lname
        fields['fname'] = fname
        fields['mname'] = mname
        fields['agrnum'] = agrnum
        payment = Payment(fields=fields)  # TODO sum ???
        r = self._request(method, request_url, headers=self._HEADERS, json=payment)
        # TODO test
        payment_info = PaymentInfo(r['PaymentInfo'])
        return payment_info

    def other_transfer(self, provider_id: str, account: str):
        """ Оплата услуги по идентификатору пользователя. Данный метод применяется для провайдеров, использующих в
        реквизитах единственный пользовательский идентификатор, без проверки номера аккаунта.
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#services

        :param provider_id: Идентификатор провайдера.
        :param account: Пользовательский идентификатор.
        :return: PaymentInfo
        """
        method = 'post'
        request_url = f'https://edge.qiwi.com/sinap/api/v2/terms/{provider_id}/payments'
        fields = dict()
        fields['account'] = account
        payment = Payment(fields=fields)  # TODO sum ???
        r = self._request(method, request_url, headers=self._HEADERS, json=payment)
        # TODO test
        payment_info = PaymentInfo(r['PaymentInfo'])
        return payment_info

    def transfer_on_details(self, name: str, extra_to_bik: str, to_bik: str, city: str, to_name: str, to_inn: str,
                            to_kpp: str, nds: str, goal: str, urgent: str, account: str, from_name: str,
                            from_name_p: str, from_name_f: str):
        """ Платеж по свободным реквизитам. Метод оплаты услуг коммерческих организаций по их банковским реквизитам.
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#freepay

        :param name: Наименование банка получателя
        :param extra_to_bik: БИК банка получателя
        :param to_bik: БИК банка получателя
        :param city: Город местонахождения получателя
        :param to_name: Наименование организации
        :param to_inn: ИНН организации
        :param to_kpp: КПП организации
        :param nds: Признак уплаты НДС. Если вы оплачиваете квитанцию и в ней не указан НДС,
        то строка НДС не облагается. В ином случае, строка В т.ч. НДС
        :param goal: Назначение платежа
        :param urgent: Признак срочного платежа (0 - нет, 1 - да). Срочный платеж выполняется от 10 минут.
        :param account: Номер счета получателя
        :param from_name: Имя плательщика
        :param from_name_p: Отчество плательщика
        :param from_name_f: Фамилия плательщика
        :return:
        """
        method = 'post'
        request_url = f'https://edge.qiwi.com/sinap/api/v2/terms/1717/payments'
        fields = dict()
        fields['name'] = name  # TODO экранировать ковычки
        fields['extra_to_bik'] = extra_to_bik
        fields['to_bik'] = to_bik
        fields['city'] = city
        fields['info'] = 'Коммерческие организации'
        fields['is_commercial'] = '1'
        fields['to_name'] = to_name  # TODO экранировать ковычки
        fields['to_inn'] = to_inn
        fields['to_kpp'] = to_kpp
        fields['nds'] = nds
        fields['goal'] = goal
        fields['urgent'] = urgent
        fields['account'] = account
        fields['from_name'] = from_name
        fields['from_name_p'] = from_name_p
        fields['from_name_f'] = from_name_f
        fields['requestProtocol'] = 'qw1'
        fields['toServiceId'] = '1717'
        payment = Payment(fields=fields)  # TODO sum ???
        r = self._request(method, request_url, headers=self._HEADERS, json=payment)
        # TODO test
        payment_info = PaymentInfo(r['PaymentInfo'])
        return payment_info

    def search_provider_by_string(self, searchPhrase: str) -> list:
        """ Поиск провайдера по строке. Поиск провайдера может понадобиться,
        если вы не знаете значения ID провайдера услуг для оплаты по идентификатору пользователя,
        либо для определения провайдера мобильной связи по номеру телефона или перевода на карту по номеру карты.
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#search

        :param searchPhrase: Строка ключевых слов для поиска провайдера.
        :return:
        """
        method = 'post'
        request_url = 'https://qiwi.com/search/results/json.action'
        headers = dict()
        headers['Accept'] = 'application/json'
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        params = dict()
        params['searchPhrase'] = searchPhrase
        return self._request(method, request_url, headers=headers, params=params)['data']

    def search_mobile_provider(self, phone_number: str):
        """ Определение мобильного оператора. Предварительное определение оператора мобильного номера выполняется
        данным запросом. В ответе возвращается идентификатор провайдера для запроса пополнения телефона.
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#search

        :param phone_number:
        :return:
        """
        method = 'post'
        request_url = 'https://qiwi.com/mobile/detect.action'
        headers = dict()
        headers['Accept'] = 'application/json'
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        data = {'phone': phone_number}
        # TODO Подумать по формату вывода
        # Ответ с HTTP Status 200 и параметром code.value = 0 or 2
        return self._request(method, request_url, headers=headers, data=data)['data']

    def search_provider_for_card(self, card_number):
        """ Поиск провайдера для перевода на карту. Определение провайдера перевода на карту выполняется
        данным запросом. В ответе возвращается идентификатор провайдера для запроса перевода на карту.
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#search

        :param card_number:
        :return:
        """
        method = 'post'
        request_url = 'https://qiwi.com/card/detect.action'
        headers = dict()
        headers['Accept'] = 'application/json'
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        data = dict()
        data['cardNumber'] = card_number
        return self._request(method, request_url, headers=headers, data=data).get('message')

    def create_p2p_token(self, keysPairName: str, serverNotificationsUrl: str = None):
        """ Выпуск токена P2P. Вы можете получить токен P2P на p2p.qiwi.com в личном кабинете, или использовать
        представленный ниже запрос. Этим запросом можно также настроить адрес уведомлений об оплате счетов.
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#search

        :param keysPairName: Название пары токенов P2P (произвольная строка).
        :param serverNotificationsUrl: URL для уведомлений об оплате счетов (необязательный параметр).
        :return: Данный запрос возвращает пару токенов P2P (для выставления счета при вызове платежной формы
        и через API, соответственно) в полях ответа PublicKey и SecretKey. Для авторизации используется токен
        API QIWI Кошелька.
        """
        method = 'post'
        request_url = 'https://edge.qiwi.com/widgets-api/api/p2p/protected/keys/create'
        json_data = dict()
        json_data['keysPairName'] = keysPairName
        json_data['serverNotificationsUrl'] = serverNotificationsUrl
        return self._request(method, request_url, headers=self._HEADERS, json=json_data)

    def list_bills(self, rows: int = None, min_creation_datetime=None, max_creation_datetime=None, next_id=None,
                   next_creation_datetime=None) -> list:
        """ Список счетов. Метод получения списка неоплаченных счетов вашего кошелька.
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#list_invoice

        :param rows: Максимальное число счетов в ответе.
        :param min_creation_datetime: Нижняя временная граница для поиска счетов, Unix-time
        :param max_creation_datetime: Верхняя временная граница для поиска счетов, Unix-time
        :param next_id: Начальный идентификатор счета для поиска.
        :param next_creation_datetime: Начальное время для поиска (возвращаются только счета,
        выставленные ранее этого времени), Unix-time.
        :return: список неоплаченных счетов вашего кошелька, соответствующих заданному фильтру
        """
        method = 'get'
        request_url = 'https://edge.qiwi.com/checkout-api/api/bill/search'
        params = dict()
        params['statuses'] = 'READY_FOR_PAY'
        params['rows'] = rows
        params['min_creation_datetime'] = min_creation_datetime
        params['max_creation_datetime'] = max_creation_datetime
        params['next_id'] = next_id
        params['next_creation_datetime'] = next_creation_datetime
        return self._request(method, request_url, headers=self._HEADERS, params=params)['bills']

    def pay_bill(self, invoice_uid: str, currency: str):
        """ Оплата счета. Выполнение безусловной оплаты счета без SMS-подтверждения.
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#paywallet_invoice
        """
        method = 'post'
        request_url = 'https://edge.qiwi.com/checkout-api/invoice/pay/wallet'
        json_data = dict()
        json_data['invoice_uid'] = invoice_uid
        json_data['currency'] = currency
        return self._request(method, request_url, headers=self._HEADERS, json=json_data)

    def reject_bill(self, id: str):
        """ Отмена неоплаченного счета. Метод отклоняет неоплаченный счет.
        При этом счет становится недоступным для оплаты.
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#search

        :param id:
        :return:
        """
        method = 'post'
        request_url = 'https://edge.qiwi.com/checkout-api/api/bill/reject'
        json_data = dict()
        json_data['id'] = id
        return self._request(method, request_url, headers=self._HEADERS, json=json_data)
