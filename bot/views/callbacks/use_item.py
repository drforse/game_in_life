from aiogram.types import CallbackQuery

from aiogram_oop_framework.views import CallbackQueryView
from game.types import Player, Item


class UseItem(CallbackQueryView):
    custom_filters = [lambda c: c.data.startswith('item use ')]
    needs_reply_auth = False
    needs_satiety_level = 0

    @classmethod
    async def execute(cls, c: CallbackQuery):
        item_id = c.data.split()[-2]
        item = Item(id=item_id)
        quantity = int(c.message.reply_markup.inline_keyboard[0][1].callback_data.split()[-2])

        player = Player(tg_id=c.from_user.id)
        player_quant = player.backpack[item_id]
        if player_quant < quantity:
            await c.answer(f'У вас столько нет :/\nВаше кол-во: {player_quant}', show_alert=True)
            return
        await player.use(item, player, quantity)

        text = f'Вы использовали {item.name}{item.emoji or ""}\nНаложенные эффекты:\n'
        for effect in item.effects:
            if effect.type == "increase":
                type_f = "+ "
            elif effect.type == "decrease":
                type_f = "- "

            text += f'  {type_f} {effect.target_characteristic} {effect.strength * quantity}' \
                    f' ({effect.duration * quantity} секунд)\n'
        await c.message.edit_text(text, reply_markup=None)
