from aiogram.types import Message, ChatType

from ......bot.views.base import UserCommandView
from ......game.types import Player


class You(UserCommandView):
    """Просмотр профиля отправителя сообщения, на которое ты реплаишь"""
    state = lambda: '*'
    needs_auth = False
    ignore_busy = True
    command_description = "see someone's profile"
    custom_filters = [lambda m: m.chat.id != ChatType.PRIVATE]

    @classmethod
    async def execute(cls, m: Message, state=None):
        player = Player(tg_id=m.reply_to_message.from_user.id)

        # TODO: create a perk to have possibility of seeing someone else's balance
        text = await player.format_info(m.chat.id, include_family=True, hide_balance=True)

        if player.photo_id:
            await m.answer_photo(player.photo_id, text)
        else:
            await m.answer(text)
