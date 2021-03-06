import logging
from aiogram.types import CallbackQuery

from aiogram_oop_framework.views import CallbackQueryView
from ....game.types import Player, Item
from ....game.exceptions import *


class BuyItem(CallbackQueryView):
    custom_filters = [lambda c: c.data.startswith('item buy ')]
    needs_reply_auth = False
    needs_satiety_level = 0

    @classmethod
    async def execute(cls, c: CallbackQuery):
        item_id = c.data.split()[-2]
        item = Item(id=item_id)
        quantity = int(c.message.reply_markup.inline_keyboard[0][1].callback_data.split()[-2])

        player = Player(tg_id=c.from_user.id)
        try:
            await item.buy(player, quantity=quantity)
        except NotEnoughMoneyOnBalance:
            await c.answer('Недостаточно денег не балансе!')
            return

        text = f'Вы купили {quantity} {item.name}{item.emoji or ""}\nЭффекты предемета:\n'
        for effect in item.effects:
            if effect.type == "increase":
                type_f = "+ "
            elif effect.type == "decrease":
                type_f = "- "
            else:
                logging.error(f'effect.type unknown {effect.type} (item: {item.id})')
                type_f = "None"

            text += f'  {type_f} {effect.target_characteristic} {effect.strength}' \
                    f' ({effect.duration} секунд)\n'
        text += f'Потрачено денег: {item.price * quantity}\n'

        await c.message.edit_text(text, reply_markup=None)
