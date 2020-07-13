from aiogram.types import Message

from ..core import Command
from ..game import Game
from game.types.player import Player


class Restart(Command):
    needs_auth = False
    needs_reply_auth = False
    needs_satiety_level = 0

    @classmethod
    async def execute(cls, m: Message):
        if m.chat.type != 'private':
            await m.answer('Эта команда работает только в лс со мной')
            return
        await cls.execute_in_private(m)

    @classmethod
    async def execute_in_private(cls, m: Message):
        player = Player(tg_id=m.from_user.id)

        if player.in_born_queue:
            await player.die()

        if not player.exists:
            await Game.process_new_user(m)
            return
        if not player.alive and not player.in_born_queue:
            await Game.process_rebornig_user(m)
            return

        if player.alive:
            await m.answer('Используй /suicide, чтобы умереть, а потом /start, чтобы заново родиться')
            return
