from aiogram_oop_framework.views import TextView
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext

from bot.aiogram_fsm import CreatePlayerForm


class GetNewPlayerGender(TextView):
    state = lambda: CreatePlayerForm.set_gender

    @classmethod
    async def execute(cls, m: Message, state: FSMContext = None, **kwargs):
        gender = m.text.lower()
        if gender not in ('мужской', 'женский', 'трансгендер'):
            await m.answer('Выберите из предложенных вариантов!')
            return
        gender_reference = {'мужской': 'male', 'женский': 'female', 'трансгендер': 'transgender'}
        async with state.proxy() as dt:
            dt['gender'] = gender_reference[gender]
        kb = InlineKeyboardMarkup()
        button = InlineKeyboardButton('Выбрать аватарку',
                                      switch_inline_query_current_chat='default userpics')
        kb.add(button)
        await m.answer('Теперь отправь аватарку для своего персонажа или выбери, нажав кнопку ниже',
                       reply_markup=kb)
        await CreatePlayerForm.next()
