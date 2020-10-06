from aiogram.types import Message

from ......bot.views.base import UserCommandView
from ......bot.game.statistics import *


class Statistics(UserCommandView):
    state = lambda: '*'
    needs_auth = False
    needs_reply_auth = False

    @classmethod
    async def execute(cls, m: Message, state=None):
        users = await get_all_users()
        chats = await get_all_chats()
        text = 'Всего игроков: %s\nВсего стран: %s' % (len(users), len(chats))
        await m.answer(text)
