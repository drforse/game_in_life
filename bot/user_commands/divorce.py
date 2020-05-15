from aiogram.types import Message

from ..core import Command
from game.types import Player


class Divorce(Command):
    needs_reply_auth = False

    @staticmethod
    async def execute(m: Message):
        player = Player(tg_id=m.from_user.id)

        partner = player.partners.get(str(m.chat.id))
        if not partner:
            await m.answer('В этой стране ты не в браке')
            return

        try:
            await m.delete()
        except:
            pass

        second_player = Player(tg_id=partner)
        await player.divorce(m.chat.id, second_player)
        await m.answer('<a href="tg://user?id=%s">%s</a> и <a href="tg://user?id=%s">%s</a> больше не вместе' %
                       (player.tg_id, player.name, second_player.tg_id, second_player.name))
