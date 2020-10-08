from aiogram.types import Message

from ......bot.views.base import UserCommandView
from ......game.types.player import Player


class Breakup(UserCommandView):
    """Команда, чтобы расстаться со своей второй половинкой.
Не забывай, что у тебя в каждом чате своя семья, так что команду нужно писать в нужном тебе чате, а не в любом)
"""
    needs_reply_auth = False
    needs_satiety_level = 10
    command_description = "breakup with your sweetheart"

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
        lover_player = Player(model_id=lover)
        await player.break_up(m.chat.id, lover_player)
        await m.answer('<a href="tg://user?id=%s">%s</a> и <a href="tg://user?id=%s">%s</a> больше не вместе' %
                       (player.tg_id, player.name, lover_player.tg_id, lover_player.name))
