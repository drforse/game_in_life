import logging
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from ..core import Command
from game.types import Player, Item
from game.exceptions import *


class BuyItem(Command):
    needs_reply_auth = False
    needs_satiety_level = 0

    @classmethod
    async def execute(cls, c: CallbackQuery):
        item_id = c.data.split()[-2]
        item = Item(id=item_id)

        player = Player(tg_id=c.from_user.id)
        try:
            await item.buy(player)
        except NotEnoughMoneyOnBalance:
            await c.answer('Недостаточно денег не балансе!')
            return

        text = f'Вы купили {item.name}{item.emoji or ""}\nЭффекты:\n'
        for effect in item.effects:
            if effect.type == "increase":
                type_f = "+ "
            elif effect.type == "decrease":
                type_f = "- "
            else:
                logging.error(f'effect.type unknown {effect.type} (item: {item.id})')
                type_f = "None"

            text += f'  {type_f} {effect.target_characteristic} {effect.strength} ({effect.duration} секунд)\n'
        text += f'Цена: {item.price}\n'

        await c.message.edit_text(text, reply_markup=None)
