from aiogram.types import Message

from ..core import Command
from ..game import Game
from game.types.player import Player


class Suicide(Command):
    needs_auth = False
    needs_reply_auth = False

    @staticmethod
    async def execute(m: Message):
        player = Player(tg_id=m.from_user.id)
        if not player.alive:
            await m.answer('А ты и так не жив')
            return

        if not player.exists:
            await m.answer('А ты и не рождался никогда даже. '
                           'Напиши мне /start в личку, чтобы начать играть :3')
            return

        await Game.process_died_user(m.bot, player)
        await m.answer('Прощай... 🕯')
