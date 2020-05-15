from aiogram.types import Message

from ..core import Command
from game.types import Player


class Breakup(Command):
    needs_reply_auth = False

    @staticmethod
    async def execute(m: Message):
        player = Player(tg_id=m.from_user.id)

        lover = player.lovers.get(str(m.chat.id))
        if not lover:
            await m.answer('В этой стране ты не состоишь в романтических отношениях')
            return

        try:
            await m.delete()
        except:
            pass
        lover_player = Player(tg_id=lover)
        await player.break_up(m.chat.id, lover_player)
        await m.answer('<a href="tg://user?id=%s">%s</a> и <a href="tg://user?id=%s">%s</a> больше не вместе' %
                       (player.tg_id, player.name, lover_player.tg_id, lover_player.name))
