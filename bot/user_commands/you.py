from aiogram.types import Message

from ..core import Command
from .me import Me


class You(Command):
    needs_reply_auth = True

    @classmethod
    async def execute(cls, m: Message, state=None):
        await Me.execute(m.reply_to_message)
