#!/usr/bin/env python
# -*- coding: utf-8 -*-

# {
#     "serviceName": "invoicing",
#     "errorCode": "auth.unauthorized",
#     "description": "Неверные аутентификационные данные",
#     "userMessage": "",
#     "datetime": "2018-04-09T18:31:42+03:00",
#     "traceId": ""
# }

# 1. В зависимости от метода поразному обрабатывать ошибки.
# 2. Можно сделать словарь с ключём по кодам ответов и dict.get(response.status_code) or Unknow Error


class QiwiException(Exception):
    pass


main_exception_codes = {'400': 'Ошибка синтаксиса запроса (неправильный формат данных)',
                        '401': 'Неверный токен или истек срок действия токена API',
                        '403': 'Нет прав на данный запрос (недостаточно разрешений у токена API)',
                        '423': 'Слишком много запросов, сервис временно недоступен',
                        '500': 'Внутренняя ошибка сервиса (превышена длина URL веб-хука, проблемы с инфраструктурой, ' \
                               'недоступность каких-либо ресурсов и т.д.'
                        }


def check_exception(response):
    # TODO make check method for choice errors dict
    return main_exception_codes.get('response.status_code') or {response.status_code: 'Неизвестная ошибка'}


# if response.status_code == 404:
#     # История платежей, Информация о транзакции, Отправка квитанции
#     message = 'Не найдена транзакция или отсутствуют платежи с указанными признаками'
#     pass
# if response.status_code == 404:
#     # Балансы, Профиль пользователя, Идентификация пользователя
#     message = 'Не найден кошелек'
#     pass
# if response.status_code == 404:
#     # Оплата / Отмена счета
#     message = 'Не найден счет'
#     pass

