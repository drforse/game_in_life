from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from ......bot.views.base import UserCommandView
from ......models import ItemModel
from ......config import PAGE_OFFSET


class Market(UserCommandView):
    needs_reply_auth = False

    @classmethod
    async def execute(cls, m: Message):
        items = ItemModel.objects()
        kb = InlineKeyboardMarkup(row_width=2)
        n = 0
        for item in items:
            button = InlineKeyboardButton(f'{item.name}{item.emoji or ""}',
                                          callback_data=f'item observe market {item.id} {m.from_user.id}')
            kb.add(button)
            n += 1
            if n == PAGE_OFFSET:
                break
        close = InlineKeyboardButton('✖', callback_data=f'close_menu {m.from_user.id}')
        if len(items) > PAGE_OFFSET:
            forward = InlineKeyboardButton('->', callback_data=f"market offset {PAGE_OFFSET} {m.from_user.id}")
            kb.row(close, forward)
        else:
            kb.row(close)

        await m.answer('Магазин:', reply_markup=kb)
