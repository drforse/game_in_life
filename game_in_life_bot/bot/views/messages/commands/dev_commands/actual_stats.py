from aiogram.types import Message

from ......bot.views.base import DevCommandView
from ......bot.game.statistics import *


class ActualStats(DevCommandView):
    state = lambda: '*'

    @classmethod
    async def execute(cls, m: Message, state=None, **kwargs):
        chats = await get_all_chats(True, m.bot)
        users = await get_all_users(chats['kicked'])
        text = 'Всего игроков: %s\nВсего стран: %s' % (len(users), len(chats) - 1)
        await m.answer(text)
