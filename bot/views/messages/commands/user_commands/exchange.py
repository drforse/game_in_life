import logging
import re
import itertools

from aiogram.types import Message

from bot.views.base import UserCommandView
from game.types import Exchange as ExchangeCore
from game.types import Player
from game.exceptions import *
import senderman_roullette_api.exceptions


class Exchange(UserCommandView):
    needs_reply_auth = False
    needs_satiety_level = 0

    @classmethod
    async def execute(cls, m: Message):
        # await m.answer('Команда временно неактивна')
        # return
        player = Player(tg_id=m.from_user.id)
        exchange = ExchangeCore(client=player)
        currencies_naming_reference = {'pasyucoin': ['паюкоин', 'пасюкоины', 'pasyucoin', 'pasyucoins'],
                                       'main': ['caffeine', 'caffeines', 'кофеин', 'кофеины'],
                                       'yulcoin': ['yulcoin', 'yulcoins', 'юлькоин', 'юлькоины']}
        possible_currencies_names = [i for i in itertools.chain(*currencies_naming_reference.values())]
        split = m.text.split()
        if len(split) == 1:
            await m.answer('Шаблон: /exchange {from_currency} {to_currency} {value}\n'
                           f'Возможные значения валют: {", ".join(possible_currencies_names)}')
        split = split[1:]
        if not re.match(r'.* .* -?[0-9]*$', ' '.join(split)):
            await m.answer('Неверый формат! шаблон: /exchange {from_currency} {to_currency} {value}')
        from_cur = split[0].lower()
        to_cur = split[1].lower()
        if from_cur not in possible_currencies_names:
            await m.answer(f'Мы не производим операций с {from_cur}, извините')
            return
        if to_cur not in possible_currencies_names:
            await m.answer(f'Мы не производим операций с {to_cur}, извините')
            return
        logging.info(f'balance: {player.balance}')
        from_cur, to_cur = cls.resolve_currency(from_cur), cls.resolve_currency(to_cur)
        try:
            await exchange.convert(from_cur, to_cur, float(split[2]))
            logging.info(f'balance after converting: {player.balance}')
            await m.answer('Операция успешна произведена.')
        except NotEnoughMoneyOnBalance:
            await m.answer('Недостаточно денег на балансе.')
        except senderman_roullette_api.exceptions.UserDoesNotExist:
            await m.answer('У Вас нет счета в юлькоинах, чтобы его открыть, зайдите в @miniroulette_bot')
        except senderman_roullette_api.exceptions.BadRequest:
            await m.answer('Обмен валют временно недоступен. '
                           'Если недоступность длится слишком долго, feel free to contact @dr_fxrse')

    @staticmethod
    def resolve_currency(currency) -> str:
        currencies_naming_reference = {'pasyucoin': ['паюкоин', 'пасюкоины', 'pasyucoin', 'pasyucoins'],
                                       'main': ['caffeine', 'caffeines', 'кофеин', 'кофеины'],
                                       'yulcoin': ['yulcoin', 'yulcoins', 'юлькоин', 'юлькоины']}
        for cur in currencies_naming_reference:
            if currency in currencies_naming_reference[cur]:
                return cur
