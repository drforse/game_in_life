from aiogram.types import Message

from ..core import Command
from game.types import Player


class Suicide(Command):
    needs_auth = False
    needs_reply_auth = False

    @staticmethod
    async def execute(m: Message):
        player = Player(tg_id=m.from_user.id)
        if not player.exists:
            await m.answer('А ты и так не жив')
            return

        await m.answer('Прощай... 🕯')
        await player.die()
