import logging

from aiogram.types import CallbackQuery
from aiogram_oop_framework.filters import filter_execute

from aiogram_oop_framework.views import CallbackQueryView

from ....game.types import Player
from ....game.types.job import Jobs
from ....models import UserModel


class CallPolice(CallbackQueryView):
    custom_filters = [lambda c: c.data.startswith('call_police')]

    @classmethod
    async def execute(cls, q: CallbackQuery, state=None, **kwargs):
        logging.warning(
            f"CallPolice.execute method was called, but it isn't expected behavior, query:\n{q}")
        await q.answer()

    @classmethod
    @filter_execute(lambda c: c.data == 'call_police theft')
    async def process_theft(cls, q: CallbackQuery):
        policemen = UserModel.objects(
            chats=q.message.chat.id, primary_job=Jobs.POLICEMAN, age__gte=0, age__lte=100)
        if not policemen:
            await q.answer("В этой стране нет полицейских (9((")
            return
        player = Player(tg_id=q.from_user.id)
        text = f"{player.name} зовет полицию: "
        tags = " ".join(f'<a href="tg://user?id={p.tg_id}">{p.name}</a>' for p in policemen)
        await q.message.reply(text + tags)
