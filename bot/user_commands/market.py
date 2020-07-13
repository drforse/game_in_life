from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from ..core import Command
from game.types import Item
from models import ItemModel


class Market(Command):
    needs_reply_auth = False
    needs_satiety_level = 0

    @classmethod
    async def execute(cls, m: Message):
        kb = InlineKeyboardMarkup()
        for item in ItemModel.objects():
            button = InlineKeyboardButton(f'{item.name}{item.emoji or ""}',
                                          callback_data=f'item observe market {item.id} {m.from_user.id}')
            kb.add(button)
        await m.answer('Магазин:', reply_markup=kb)
