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


class QiwiMainException(Exception):
    pass


exception_codes = {'400': 'Ошибка синтаксиса запроса (неправильный формат данных)',
                   '401': 'Неверный токен или истек срок действия токена API',
                   }
#
# if response.status_code == 400:
#     # all
#     message = 'Ошибка синтаксиса запроса (неправильный формат данных)'
#     pass
# if response.status_code == 401:
#     # all
#     message = 'Неверный токен или истек срок действия токена API'
#     pass
# if response.status_code == 403:
#     # all
#     message = 'Нет прав на данный запрос (недостаточно разрешений у токена API)'
#     pass
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
# if response.status_code == 423:
#     # all
#     message = 'Слишком много запросов, сервис временно недоступен'
#     pass
# if response.status_code == 500:
#     # all
#     message = 'Внутренняя ошибка сервиса (превышена длина URL веб-хука, проблемы с инфраструктурой, ' \
#               'недоступность каких-либо ресурсов и т.д.'





