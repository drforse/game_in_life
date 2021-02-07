from aiogram.types import Message

from ......bot.views.base import UserCommandView
from ......game.types.player import Player, Eva, Adam
from ......senderman_roullette_api import exceptions as sexcs


class Me(UserCommandView):
    """Просмотр своего профиля"""
    state = lambda: '*'
    needs_reply_auth = False
    ignore_busy = True

    command_description = "see your profile"
    set_my_commands = 'first'

    @classmethod
    async def execute(cls, m: Message, state=None):
        player = Player(tg_id=m.from_user.id)

        if m.chat.type == "private":
            text = await player.format_info()
        else:
            text = await player.format_info(m.chat.id, include_family=True)

        if player.photo_id:
            await m.answer_photo(player.photo_id, text)
        else:
            await m.answer(text)
