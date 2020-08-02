from aiogram.types import CallbackQuery, InlineKeyboardButton

from aiogram_oop_framework.views import CallbackQueryView


class ChangeItemQuantity(CallbackQueryView):
    custom_filters = [lambda c: c.data.startswith('item quantity change ')]
    needs_reply_auth = False
    needs_satiety_level = 0

    @classmethod
    async def execute(cls, c: CallbackQuery):
        for l in c.message.reply_markup.inline_keyboard:
            print([b.as_json() for b in l])
        change_type = c.data.split()[-2]
        quantity_b_data = c.message.reply_markup.inline_keyboard[0][1].callback_data
        current_quantity = int(quantity_b_data.split()[-2])
        print(quantity_b_data)
        print(current_quantity)

        if change_type == '-':
            new_quantity = current_quantity - 1
        else:
            new_quantity = current_quantity + 1
        if new_quantity < 1:
            await c.answer('Количество не может быть меньше одного', show_alert=True)
            return
        markup = c.message.reply_markup
        new_quant_b = InlineKeyboardButton(str(new_quantity),
                                           callback_data=quantity_b_data.replace(f' {current_quantity} ',
                                                                                 f' {new_quantity} '))
        markup.inline_keyboard[0][1] = new_quant_b

        await c.answer()
        await c.message.edit_reply_markup(markup)
