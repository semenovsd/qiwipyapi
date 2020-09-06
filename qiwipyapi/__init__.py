#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2020 qiwipyapi
# Written by Stanislav Semenov
# https://github.com/semenovsd/qiwipyapi

from qiwipyapi.wallets import P2PWallet, QIWIWallet


class Wallet:
    """ Класс создаёт кошелёк для P2P API или QIWI API.
        https://qiwi.com/api
        https://developer.qiwi.com/ru/p2p-payments

    :param wallet_number:
    :param wallet_token:
    :param p2p_sec_key:
    :return: Object QIWIWallet or P2PWallet
    """
    def __new__(cls, wallet_number, wallet_token=None, p2p_sec_key=None):
        if wallet_token:
            return QIWIWallet(wallet_number, token=wallet_token)
        elif p2p_sec_key:
            return P2PWallet(wallet_number, token=p2p_sec_key)
        else:
            raise AttributeError('Enter wallet_token or p2p_token')
