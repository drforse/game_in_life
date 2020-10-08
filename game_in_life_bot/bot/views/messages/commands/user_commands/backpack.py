from bson import ObjectId

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from ......bot.views.base import UserCommandView
from ......config import PAGE_OFFSET
from ......game.types import Player, Item


class Backpack(UserCommandView):
    needs_reply_auth = False

    @classmethod
    async def execute(cls, m: Message):
        player = Player(tg_id=m.from_user.id)
        items = player.backpack.items()
        kb = InlineKeyboardMarkup()
        n = 0
        for item_id, item_quantity in items:
            if item_quantity <= 0:
                continue
            item = Item(id=ObjectId(item_id))
            item.update_from_db()
            button = InlineKeyboardButton(f'{item.emoji or ""} {item.name} {item_quantity}',
                                          callback_data=f'item observe backpack {item_id} {m.from_user.id}')
            kb.add(button)
            n += 1
            if n == PAGE_OFFSET:
                break

        close = InlineKeyboardButton('✖', callback_data=f'close_menu {m.from_user.id}')
        if len(items) > PAGE_OFFSET:
            forward = InlineKeyboardButton('->', callback_data=f"backpack offset {PAGE_OFFSET} {m.from_user.id}")
            kb.row(close, forward)
        else:
            kb.row(close)
        await m.answer('Ваш рюкзак:', reply_markup=kb)
