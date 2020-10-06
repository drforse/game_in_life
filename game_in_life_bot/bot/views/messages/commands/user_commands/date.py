from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from ......bot.views.base import UserCommandView
from ......game.types.player import *


class Date(UserCommandView):
    needs_satiety_level = 5

    @staticmethod
    async def execute(m: Message):
        player_user = m.from_user
        player = Player(tg_id=player_user.id)
        lover_user = m.reply_to_message.from_user
        lover_player = Player(tg_id=lover_user.id)

        can_date = await player.can_date(m.chat.id, lover_player)

        if not can_date['result']:
            await m.answer(player.cant_date_reason_exaplanation[can_date['reason']])
            return

        try:
            await m.delete()
        except:
            pass

        kb = InlineKeyboardMarkup()
        accept = InlineKeyboardButton('Принять', callback_data=f'action dating accept {player.tg_id} {lover_player.tg_id}')
        decline = InlineKeyboardButton('Отклонить',
                                       callback_data=f'action dating decline {player.tg_id} {lover_player.tg_id}')
        kb.add(accept, decline)

        await m.answer(
            '%s, %s предлагает тебе встречаться ' % (
                player_user.get_mention(player.name), lover_user.get_mention(lover_player.name)),
            reply_markup=kb)
