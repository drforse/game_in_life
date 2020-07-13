from datetime import datetime
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from ..core import Command
from game.types import Player, Item


class UseItem(Command):
    needs_reply_auth = False
    needs_satiety_level = 0

    @classmethod
    async def execute(cls, c: CallbackQuery):
        item_id = c.data.split()[-2]
        item = Item(id=item_id)

        player = Player(tg_id=c.from_user.id)
        await player.use(item, player)

        text = f'Вы использовали {item.name}{item.emoji or ""}\nНаложенные эффекты:\n'
        for effect in item.effects:
            if effect.type == "increase":
                type_f = "+ "
            elif effect.type == "decrease":
                type_f = "- "

            text += f'  {type_f} {effect.target_characteristic} {effect.strength} ({effect.duration} секунд)\n'
        await c.message.edit_text(text, reply_markup=None)
