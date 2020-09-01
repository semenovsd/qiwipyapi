#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import logging
# TODO different levels logs
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
import uuid
import requests
from requests import RequestException

from .exceptions import QiwiException, check_exception


class Wallet:
    """ Класс для работы с QIWI Wallet API и QIWI P2P API.
    Поддерживает все методы и параметры api:
    https://qiwi.com/api
    https://developer.qiwi.com/ru/p2p-payments

    :param _WALLET_NUMBER: Qiwi wallet number in format 79219876543 without +
    :param _WALLET_TOKEN: Qiwi wallet token
    :param _P2P_SEC_KEY: Ключи создаются в личном кабинете в разделе "API" (на сайте p2p.qiwi.com)
    :return: New wallet
    """

    def __init__(self, wallet_number, wallet_token=None, p2p_sec_key=None):
        try:
            assert wallet_token or p2p_sec_key
        except AssertionError:
            raise AssertionError('Enter wallet_token and/or p2p_token')
        else:
            self._WALLET_NUMBER = wallet_number
            if wallet_token:
                self._WALLET_TOKEN = wallet_token
                self._HEADERS = {'Accept': 'application/json',
                                 'Content-Type': 'application/json',
                                 'Authorization': f'Bearer {wallet_token}'}
            if p2p_sec_key:
                self._P2P_SEC_KEY = p2p_sec_key
                self._P2P_HEADERS = {'Accept': 'application/json',
                                     'Content-Type': 'application/json',
                                     'Authorization': f'Bearer {p2p_sec_key}'}
            self._session = requests.Session()
            # TODO add timeout and proxy

    def _request(self, method, request_url, **kwargs):
        """ Запрос на сервер API

        :param method:
        :param request_url:
        :param kwargs:
        :return:
        :raises:
            RequestException: if some errors in request
        """
        try:
            response = self._session.request(method=method, url=request_url, headers=kwargs.get('headers'),
                                             params=kwargs.get('params'), data=kwargs.get('data'),
                                             json=kwargs.get('json'))
        except RequestException as e:
            raise RequestException(e, method, request_url, kwargs)
        else:
            return self._response(response)

    def _response(self, response):
        """ Обработка ответа

        :param response:
        :return:
        :raises:
            QiwiException: if some errors in response
        """
        if response.status_code == 200 or response.status_code == 201:
            try:
                response_json = response.json()
                return response_json
            except AttributeError:
                return response
        else:
            e = check_exception(response)
            raise QiwiException(e, response, self._session.params)

    # P2P QIWI API
    def create_invoice(self, amount: dict, bill_id=None,
                       expiration_date_time=datetime.now(tz=tzlocal()) + timedelta(hours=8), **kwargs):
        """ Выставить новый счёт
        https://developer.qiwi.com/ru/p2p-payments/#create

        :param amount: данные о сумме счета
        :param bill_id: уникальный идентификатор счета в вашей системе
        :param expiration_date_time:
        :param kwargs: дополнительные параметры
        :return: ??? подумать, что именно возвращать (урл или весь ответ) или вообще отдавать объект
        """
        method = 'put'
        request_url = f'https://api.qiwi.com/partner/bill/v1/bills/{bill_id if bill_id else uuid.uuid1()}'
        json_data = dict()
        json_data.update(amount)
        json_data['expirationDateTime'] = expiration_date_time.strftime('%Y-%m-%dT%H:%m:%S+00:00')
        json_data.update(kwargs)
        # При выставление счёта в ответе приходит payUrl к ссылке можно добавить параметры:
        # https: // developer.qiwi.com / ru / p2p - payments /  # option
        # paySource
        # allowedPaySources
        # successUrl
        # lifetime
        return self._request(method, request_url, headers=self._P2P_HEADERS, json=json_data)

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
        # TODO возвращать данные по счёту в случае успеха и кидать ошибку, если такого счёта нет.
        return self._request(method, request_url, headers=self._P2P_HEADERS)

    def cancel_invoice(self, bill_id):
        """ Отмена счёта
        https://developer.qiwi.com/ru/p2p-payments/#cancel

        :param bill_id: уникальный идентификатор счета в вашей системе.
        :return:
        """
        method = 'post'
        request_url = f'https://api.qiwi.com/partner/bill/v1/bills/{bill_id}/reject'
        # TODO возвращать True в случае успеха и кидать ошибку, если такого счёта нет.
        return self._request(method, request_url, headers=self._P2P_HEADERS)

    # Wallet Qiwi API
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
        params = f'authInfoEnabled={authInfoEnabled}&' \
                 f'contractInfoEnabled={contractInfoEnabled}&' \
                 f'userInfoEnabled={userInfoEnabled}'
        request_url = f'/person-profile/v1/profile/current'
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
        request_url = f'/identification/v1/persons/{self._WALLET_NUMBER}/identification'
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
        request_url = f'/identification/v1/persons/{self._WALLET_NUMBER}/identification'
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
        request_url = f'/qw-limits/v1/persons/{self._WALLET_NUMBER}/actual-limits'
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
        request_url = f'person-profile/v1/persons/{self._WALLET_NUMBER}/status/restrictions'
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
        return self._request(method, request_url, headers=self._HEADERS, params=params).get('data')

    def search_provider_for_card(self, card_number):
        """ Поиск провайдера для перевода на карту
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

    def payment_to_card(self, card_number, provider_id, **kwargs):
        """ Перевод на карту
        https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#cards

        :param card_number:
        :param provider_id:
        :param kwargs:
        :return:
        """
        method = 'post'
        request_url = f'https://edge.qiwi.com/sinap/api/v2/terms/{provider_id}/payments'
        json_data = dict()
        json_data['id'] = kwargs.get('id') or str(uuid.uuid1())
        json_data['paymentMethod'] = kwargs.get('paymentMethod') or {'type': 'Account', 'accountId': '643'}
        json_data['fields'] = dict()
        json_data['fields']['account'] = card_number
        json_data.update(kwargs)
        # TODO кидать ошибку, если не хватает денег и всё что не связанно с корректностью данных
        return self._request(method, request_url, headers=self._HEADERS, json=json_data).get('PaymentInfo')

    # def Список балансов https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#balances_list

    # def Создание баланса https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#balance_create

    # Запрос доступных счетов https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#funding_offer

    # Установка баланса по умолчанию https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#default_balance

    # Статистика платежей https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#stat

    # Информация о транзакции https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#txn_info

    # def Квитанция платежа https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#payment_receipt

    # def Информация о транзакции
    #     Есть отдельные ошибки описанные в https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#search

    # def check_commission(self):
    # Узнать комиссию https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#rates

    # def Предзаполненная форма платежа https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#autocomplete

    # Как узнать свой никнейм через API https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#autocomplete

    # Перевод на киви кошелёк https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#p2p

    # Конвертировать средства https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#CCY

    # Курсы валют https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#exchange

    # Оплата сотовой связи https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#cell

    # Банковский перевод https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#banks

    # Перевод по номеру счета/договора https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#banks

    # Оплата других услуг https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#services

    # Платеж по свободным реквизитам https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#freepay

    # Поиск провайдера по строке https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#search

    # Определение мобильного оператора https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#search

    # Выпуск токена P2P https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#search

    # Список счетов https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#search

    # Оплата счета https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#search

    # Отмена неоплаченного счета https://developer.qiwi.com/ru/qiwi-wallet-personal/index.html#search

    # Web Hooks ???
