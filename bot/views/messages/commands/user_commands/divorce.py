from aiogram.types import Message

from bot.views.base import UserCommandView
from game.types.player import Player


class Divorce(UserCommandView):
    needs_reply_auth = False
    needs_satiety_level = 35

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

        second_player = Player(model_id=partner)
        await player.divorce(m.chat.id, second_player)
        await m.answer('<a href="tg://user?id=%s">%s</a> и <a href="tg://user?id=%s">%s</a> больше не вместе' %
                       (player.tg_id, player.name, second_player.tg_id, second_player.name))
