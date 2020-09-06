# QiwiPyAPI
Библиотека для простой работы с QIWI Wallet API и/или QIWI P2P API. 
Поддерживает все запросы QIWI P2P API и большинство QIWI Wallet API.

# Installation
pip install qiwipyapi

# Use
from qiwipyapi import Wallet

QIWI_SEC_TOKEN = '***'
QIWI_TOKEN = '***'
wallet_number = '***' \# without +
cc_number = '***'

\# For qiwi wallet
wallet = Wallet(wallet_number, wallet_token=QIWI_TOKEN)

\# For p2p qiwi wallet
wallet_p2p = Wallet(wallet_number, p2p_sec_key=QIWI_SEC_TOKEN)

# Методы P2P Qiwi API
Выставить счет для оплаты:

invoice = wallet_p2p.create_invoice(value=10)
print(invoice['payUrl']) # выводи ссылку на форму оплаты счёта

\# также можно получить доступ ко всем параметрам счёта
print(invoice['sum']['amount'])  # сумма счёта
print(invoice['comment'])  # комментарии к счёту

\# Проверить стату счёта
status = wallet_p2p.invoice_status(bill_id=invoice['billId'])

\# Отменить выставленный счёт
wallet_p2p.cancel_invoice(bill_id=invoice['billId'])


# Методы Qiwi wallet API

\# Узнать балансы по кошельку
balances = wallet.list_balances()
\# Балансы по всем счетам
print(balances['accounts'])
\# Баланс по конкретному счету
amount = balances['accounts'][0]['balance']['amount']
print(amount)

\# Узнать провайдера для перевода на карту
provider_id = wallet.search_provider_for_card(card_number=cc_number)
print(provider_id)

\# Узнать коммиссию за перевод
commission = wallet.get_commission(id=provider_id, amount=amount)
print(commission)

\# Сделать перевод на карту
payment = wallet.payment_to_card(amount=amount, card_number=cc_number, provider_id=provider_id)
print(payment)
