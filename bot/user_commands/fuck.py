from aiogram.types import Message

from ..core import Command
from ..game import Game
from models import *


class Fuck(Command):

    @classmethod
    async def execute(cls, m: Message):

        user = User.objects(tg_id=m.from_user.id, age__gte=0, age__lte=100)
        if not user:
            await m.answer('Вы не играете. Чтобы начать напишите мне /start в лс')
            return

        if m.reply_to_message:
            second_user = User.objects(tg_id=m.reply_to_message.from_user.id, age__gte=0, age__lte=100)
            if not second_user:
                await m.answer('Пользователь не играет.')
                return
        else:
            second_user = user

        user = user[0]
        second_user = second_user[0]
        current_state = await (cls.dp.current_state(chat=m.chat.id, user=m.from_user.id)).get_state()
        if current_state:
            await m.answer('Вообще-то сейчас ты занят делом :3')

        await Game.process_fuck(cls.dp, m, user, second_user)
