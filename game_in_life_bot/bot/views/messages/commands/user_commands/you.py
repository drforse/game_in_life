from aiogram.types import Message

from ......bot.views.base import UserCommandView
from .me import Me


class You(UserCommandView):
    state = lambda: '*'
    needs_auth = False

    @classmethod
    async def execute(cls, m: Message, state=None):
        await Me.execute(m.reply_to_message)
