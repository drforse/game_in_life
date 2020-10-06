from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from .base.action import BaseAction
from ......bot.views.base import UserCommandView
from ......game.types.player import *


class Date(UserCommandView, BaseAction):
    needs_satiety_level = 5

    @classmethod
    async def execute(cls, m: Message):
        player = Player(tg_id=m.from_user.id)
        lover_player = Player(tg_id=m.reply_to_message.from_user.id)

        can_date = await player.can_date(m.chat.id, lover_player)

        if not can_date['result']:
            await m.answer(player.cant_date_reason_exaplanation[can_date['reason']])
            return

        args = m.get_args()
        m.text = '/action' + ' type:dating '
        m.text += args or 'выстречаться |'
        await cls.execute_action(m)
