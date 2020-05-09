from aiogram.types import Message

from ..core import Command
from models import *


class Divorce(Command):

    @staticmethod
    async def execute(m: Message):
        user = User.get(tg_id=m.from_user.id, age__gte=0, age__lte=100)
        if not user:
            await m.answer('Ты не жив, напиши /start мне в лс, чтобы родиться')
            return

        partner = user.partners.get(str(m.chat.id))
        if not partner:
            await m.answer('В этой стране ты не в браке')
            return
        user.unset_partner(m.chat.id)
        second_user = User.objects(pk=partner)[0]
        second_user.unset_partner(m.chat.id)
        await m.answer('<a href="tg://user?id=%s">%s</a> и <a href="tg://user?id=%s">%s</a> больше не вместе' %
                       (user.tg_id, user.name, second_user.tg_id, second_user.name))
