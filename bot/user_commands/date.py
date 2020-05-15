from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from .base.action import BaseAction
from game.types import *


class Date(BaseAction):

    @staticmethod
    async def execute(m: Message):
        player = Player(tg_id=m.from_user.id)
        lover_player = Player(tg_id=m.reply_to_message.from_user.id)

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

        await m.answer('<a href="tg://user?id=%d">%s</a>, <a href="tg://user?id=%d">%s</a> предлагает тебе встречаться '
                       % (lover_player.tg_id, lover_player.name, player.tg_id, player.name),
                       reply_markup=kb)
