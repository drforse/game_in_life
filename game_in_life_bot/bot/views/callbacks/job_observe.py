import logging
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from aiogram_oop_framework.views import CallbackQueryView
from bson import ObjectId

from ....game.types.job import Job


class ObserveJob(CallbackQueryView):
    custom_filters = [lambda c: c.data.startswith('job observe ')]
    needs_satiety_level = 0

    @classmethod
    async def execute(cls, c: CallbackQuery):
        data = c.data.split()
        job_id = data[-2]
        kb = InlineKeyboardMarkup()

        apply_button = InlineKeyboardButton(
            'Наняться', callback_data=f'job get {job_id} {c.from_user.id}')
        kb.add(apply_button)
        quit_button = InlineKeyboardButton(
            'Уволиться', callback_data=f'job quit {job_id} {c.from_user.id}')
        kb.add(quit_button)

        job = Job(id=job_id)
        text = f'{job.title}\nПерки:\n'
        for level in job.new_perks_by_job_level:
            text += f"Ур. {level}: "
            perk_titles = [perk.title for perk in job.new_perks_by_job_level[level]]
            text += ", ".join(perk_titles)

        await c.message.edit_text(text, reply_markup=kb)
