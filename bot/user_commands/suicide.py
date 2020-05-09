from aiogram.types import Message

from ..core import Command
from ..game import Game
from models import *


class Suicide(Command):

    @staticmethod
    async def execute(m: Message):
        user = User.objects(tg_id=m.from_user.id, age__gte=0, age__lte=100)
        if not user:
            await m.answer('А ты и так не жив')
            return
        user = user[0]
        user.age = 101
        user.save()
        await m.answer('Прощай... 🕯')
        await Game.process_died_user(m.bot, user)
