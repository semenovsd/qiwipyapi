# QiwiPyAPI
Библиотека для простой работы с QIWI Wallet API и/или QIWI P2P API. 
Поддерживает все запросы QIWI P2P API и большинство QIWI Wallet API.

# Installation
pip install qiwipyapi

# Use
from qiwipyapi import Wallet

\# для работы с QIWI Wallet API - wallet_toke и/или для QIWI P2P APi - p2p_sec_key

\# For qiwi wallet

wallet = Wallet(wallet_number,  wallet_token=wallet_token)

\# For p2p qiwi wallet

wallet = Wallet(wallet_number,  p2p_sec_key=p2p_sec_key)

# Методы P2P Qiwi API
Выставить счет для оплаты:

invoice = wallet.create_invoice()
print(invoice)  # выводи ссылку на форму оплаты счёта

\# также можно получить доступ ко всем параметрам счёта
print(invoice['sum']['amount'])  # сумма счёта
print(invoice['comment'])  # комментарии к счёту


# Проверить стату счёта

status = wallet.invoice_status(bill_id=invoice['billId'])

# Отменить выставленный счёт

wallet.cancel_invoice(bill_id=invoice['billId'])


