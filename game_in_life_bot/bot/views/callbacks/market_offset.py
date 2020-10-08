from aiogram.types import CallbackQuery,  InlineKeyboardMarkup, InlineKeyboardButton

from aiogram_oop_framework.views import CallbackQueryView

from ....models import ItemModel
from ....config import PAGE_OFFSET


class UseItem(CallbackQueryView):
    custom_filters = [lambda c: c.data.startswith("market offset")]
    needs_reply_auth = False
    needs_satiety_level = 0

    @classmethod
    async def execute(cls, c: CallbackQuery):
        offset = int(c.data.split()[-2])

        items = ItemModel.objects()
        kb = InlineKeyboardMarkup(row_width=2)
        n = 0
        for item in items[offset:]:
            button = InlineKeyboardButton(f'{item.name}{item.emoji or ""}',
                                          callback_data=f'item observe market {item.id} {c.from_user.id}')
            kb.add(button)
            n += 1
            if n == PAGE_OFFSET:
                break
        close = InlineKeyboardButton('✖', callback_data=f"close_menu {c.from_user.id}")
        backward = InlineKeyboardButton('<-', callback_data=f"market offset {offset - PAGE_OFFSET} {c.from_user.id}")
        forward = InlineKeyboardButton('->', callback_data=f"market offset {offset + PAGE_OFFSET} {c.from_user.id}")
        buttons = [close]
        if offset > 0:
            buttons.insert(0, backward)
        if len(items) > offset + PAGE_OFFSET:
            buttons.append(forward)
        kb.row(*buttons)

        await c.message.edit_reply_markup(reply_markup=kb)
