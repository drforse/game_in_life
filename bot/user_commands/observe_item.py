import logging
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from ..core import Command
from game.types import Item


class ObserveItem(Command):
    needs_reply_auth = False
    needs_satiety_level = 0

    @classmethod
    async def execute(cls, c: CallbackQuery):
        data = c.data.split()
        item_id = data[-2]
        kb = InlineKeyboardMarkup()
        if data[2] == 'backpack':
            use_button = InlineKeyboardButton('Использовать',
                                              callback_data=f'item use {item_id} {c.from_user.id}')
            kb.add(use_button)
        elif data[2] == 'market':
            buy_button = InlineKeyboardButton('Купить',
                                              callback_data=f'item buy {item_id} {c.from_user.id}')
            kb.add(buy_button)
        item = Item(id=item_id)
        text = f'{item.name}{item.emoji or ""}\nЭффекты:\n'
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
        await c.message.edit_text(text, reply_markup=kb)
