from bson import ObjectId

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from bot.views.base import UserCommandView
from game.types import Player, Item


class Backpack(UserCommandView):
    needs_reply_auth = False
    needs_satiety_level = 0

    @classmethod
    async def execute(cls, m: Message):
        player = Player(tg_id=m.from_user.id)
        kb = InlineKeyboardMarkup()
        for item_id, item_quantity in player.backpack.items():
            if item_quantity <= 0:
                continue
            item = Item(id=ObjectId(item_id))
            item.update_from_db()
            button = InlineKeyboardButton(f'{item.name}{item.emoji or ""}: {item_quantity}',
                                          callback_data=f'item observe backpack {item_id} {m.from_user.id}')
            kb.add(button)
        await m.answer('Ваш рюкзак:', reply_markup=kb)
