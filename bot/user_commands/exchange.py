import logging
import re
import itertools

from aiogram.types import Message

from ..core import Command
from game.types import Exchange as ExchangeCore
from game.types import Player
from game.exceptions import *


class Exchange(Command):
    needs_reply_auth = False

    @classmethod
    async def execute(cls, m: Message):
        await m.answer('Команда временно неактивна')
        player = Player(tg_id=m.from_user.id)
        exchange = ExchangeCore(client=player)
        try:
            currencies_naming_reference = {'pasyucoin': ['паюкоин', 'пасюкоины', 'pasyucoin', 'pasyucoins'],
                                           'main': ['main', 'основная']}
            possible_currencies_names = itertools.chain(*currencies_naming_reference.values())
            split = m.text.split()
            if len(split) == 1:
                await m.answer('Шаблон: /exchange {from_currency} {to_currency} {value}\n'
                               f'Возможные значения валют: {", ".join(possible_currencies_names)}')
            split = split[1:]
            if not re.match(r'.* .* [0-9]*$', ' '.join(split)):
                await m.answer('Неверый формат! шаблон: /exchange {from_currency} {to_currency} {value}')
            from_cur = split[0]
            to_cur = split[1]
            if from_cur not in possible_currencies_names:
                await m.answer(f'Мы не производим операций с {from_cur}, извините')
                return
            if to_cur not in possible_currencies_names:
                await m.answer(f'Мы не производим операций с {to_cur}, извините')
                return
            logging.info(f'balance: {player.balance}')
            from_cur, to_cur = cls.resolve_currency(from_cur), cls.resolve_currency(to_cur)
            await exchange.convert(from_cur, to_cur, float(split[2]))
            logging.info(f'balance after converting: {player.balance}')
            await m.answer('Операция успешна произведена.')
        except NotEnoughMoneyOnBalance:
            await m.answer('Недостаточно денег на балансе.')

    @staticmethod
    def resolve_currency(currency) -> str:
        currencies_naming_reference = {'pasyucoin': ['паюкоин', 'пасюкоины', 'pasyucoin', 'pasyucoins'],
                                       'main': ['main', 'основная']}
        for cur in currencies_naming_reference:
            if currency in currencies_naming_reference[cur]:
                return cur
