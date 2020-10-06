from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from .base.action import BaseAction
from ......bot.views.base import UserCommandView
from ......game.types.player import *


class Marry(UserCommandView, BaseAction):
    needs_satiety_level = 10

    @classmethod
    async def execute(cls, m: Message):
        player = Player(tg_id=m.from_user.id)
        partner_player = Player(tg_id=m.reply_to_message.from_user.id)

        can_marry = await player.can_marry(m.chat.id, partner_player)

        if not can_marry['result']:
            await m.answer(player.cant_marry_reason_exaplanation[can_marry['reason']])
            return

        args = m.get_args()
        m.text = '/action' + ' type:marriage '
        m.text += args or 'тебе свои руку и сердце |'
        await cls.execute_action(m)
