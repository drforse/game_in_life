import logging
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from aiogram_oop_framework.views import CallbackQueryView
from bson import ObjectId

from ....config import UNEMPLOYED_JOB_ID
from ....game.types.job import Job
from ....game.types import Player


class GetJob(CallbackQueryView):
    custom_filters = [lambda c: c.data.startswith('job get ')]
    needs_satiety_level = 0

    @classmethod
    async def execute(cls, c: CallbackQuery):
        data = c.data.split()
        job_id = data[-2]
        player = Player(tg_id=c.from_user.id)
        job = Job(id=job_id)
        kb = InlineKeyboardMarkup()

        if player.primary_job.id != UNEMPLOYED_JOB_ID:
            await c.answer("Вы уже работаете, сменить работу невозможно азаза")
            # TODO:
            #  [] смена работы
            return
        await player.get_job(job)

        await c.message.edit_text(f"Вы нанялись на работу {job.title}", reply_markup=kb)
