from aiogram.types import CallbackQuery,  InlineKeyboardMarkup, InlineKeyboardButton

from aiogram_oop_framework.views import CallbackQueryView
from bson import ObjectId

from ....game.types import Player, Item
from ....config import PAGE_OFFSET


class UseItem(CallbackQueryView):
    custom_filters = [lambda c: c.data.startswith("backpack offset")]
    needs_reply_auth = False
    needs_satiety_level = 0

    @classmethod
    async def execute(cls, c: CallbackQuery):
        offset = int(c.data.split()[-2])

        player = Player(tg_id=c.from_user.id)
        items = list(player.backpack.items())
        kb = InlineKeyboardMarkup(row_width=2)
        n = 0
        for item_id, item_quantity in items[offset:]:
            if item_quantity <= 0:
                continue
            item = Item(id=ObjectId(item_id))
            item.update_from_db()
            button = InlineKeyboardButton(f'{item.emoji or ""} {item.name} {item_quantity}',
                                          callback_data=f'item observe backpack {item_id} {c.from_user.id}')
            kb.add(button)
            n += 1
            if n == PAGE_OFFSET:
                break
        close = InlineKeyboardButton('✖', callback_data=f"close_menu {c.from_user.id}")
        backward = InlineKeyboardButton('<-', callback_data=f"backpack offset {offset - PAGE_OFFSET} {c.from_user.id}")
        forward = InlineKeyboardButton('->', callback_data=f"backpack offset {offset + PAGE_OFFSET} {c.from_user.id}")
        buttons = [close]
        if offset > 0:
            buttons.insert(0, backward)
        if len(items) > offset + PAGE_OFFSET:
            buttons.append(forward)
        kb.row(*buttons)

        await c.message.edit_reply_markup(reply_markup=kb)
