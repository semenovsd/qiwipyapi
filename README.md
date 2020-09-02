# QiwiPyAPI
Библиотека для простой работы с QIWI Wallet API и/или QIWI P2P API. 
Поддерживает все запросы QIWI P2P API и большинство QIWI Wallet API.

# Installation
pip install qiwipyapi

# Use
from qiwipyapi import Wallet

\# для работы с QIWI Wallet API - wallet_toke и/или для QIWI P2P APi - p2p_sec_key

wallet = Wallet(wallet_number, wallet_token, p2p_sec_key)

# Методы P2P Qiwi API
Выставить счет для оплаты:

bill = wallet.create_bill()
print(bill['payUrl'])  # link to payment from

# Проверить стату счёта


# Отменить выставленный счёт

