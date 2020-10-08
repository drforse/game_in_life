from aiogram.types import Message

from ......bot.views.base import UserCommandView
from .me import Me


class You(UserCommandView):
    """Просмотр профиля отправителья сообщения, на которое ты реплаишь"""
    state = lambda: '*'
    needs_auth = False
    ignore_busy = True
    command_description = "see someone's profile"

    @classmethod
    async def execute(cls, m: Message, state=None):
        await Me.execute(m.reply_to_message)
