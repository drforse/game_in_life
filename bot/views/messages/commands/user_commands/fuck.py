from aiogram.types import Message

from bot.views.base import UserCommandView
from .base.action import BaseAction


class Fuck(UserCommandView):
    needs_satiety_level = 65

    @classmethod
    async def execute(cls, m: Message):
        args = m.get_args()
        m.text = '/action' + ' type:fuck '
        m.text += args or 'поебаться |'
        await BaseAction.execute(m)
