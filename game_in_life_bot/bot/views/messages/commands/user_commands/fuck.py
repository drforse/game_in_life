from aiogram.types import Message

from game_in_life_bot.bot.views.base import UserCommandView
from .base.action import BaseAction


class Fuck(UserCommandView, BaseAction):
    needs_satiety_level = 15

    @classmethod
    async def execute(cls, m: Message, state=None, **kwargs):
        args = m.get_args()
        m.text = '/action' + ' type:fuck '
        m.text += args or 'поебаться |'
        await cls.execute_action(m)
