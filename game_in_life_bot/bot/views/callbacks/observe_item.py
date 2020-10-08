import logging
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from aiogram_oop_framework.views import CallbackQueryView
from ....game.types import Item


class ObserveItem(CallbackQueryView):
    custom_filters = [lambda c: c.data.startswith('item observe ')]
    needs_reply_auth = False
    needs_satiety_level = 0

    @classmethod
    async def execute(cls, c: CallbackQuery):
        data = c.data.split()
        item_id = data[-2]
        kb = InlineKeyboardMarkup()
        decrease_quant_b = InlineKeyboardButton('-', callback_data=f'item quantity change - {c.from_user.id}')
        increase_quant_b = InlineKeyboardButton('+', callback_data=f'item quantity change + {c.from_user.id}')
        chosen_quant_b = InlineKeyboardButton('1', callback_data=f'item quantity chosen 1 {c.from_user.id}')
        kb.row(decrease_quant_b, chosen_quant_b, increase_quant_b)

        close = InlineKeyboardButton('✖', callback_data=f"close_menu {c.from_user.id}")
        bottom_row = [close]
        if data[2] == 'backpack':
            use_button = InlineKeyboardButton('Использовать',
                                              callback_data=f'item use {item_id} {c.from_user.id}')
            bottom_row.append(use_button)
        elif data[2] == 'market':
            buy_button = InlineKeyboardButton('Купить',
                                              callback_data=f'item buy {item_id} {c.from_user.id}')
            bottom_row.append(buy_button)
        kb.row(*bottom_row)

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
