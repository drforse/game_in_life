from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from ......models import JobModel
from ......bot.views.base import UserCommandView


class GetJob(UserCommandView):
    """Наймись на работу"""
    needs_reply_auth = False

    commands = ["get_job"]
    command_description = "get yourself a job"

    @classmethod
    async def execute(cls, m: Message):
        await m.answer("Not ready yet!")
        return

        kb = InlineKeyboardMarkup()
        jobs = JobModel.objects()
        for job in jobs:
            kb.add(InlineKeyboardButton(
                job.title, callback_data=f"job observe {job.id} {m.from_user.id}"))
        await m.answer("Выбери подходящую себе работу", reply_markup=kb)
