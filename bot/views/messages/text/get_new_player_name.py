from aiogram_oop_framework.views import TextView
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext

from bot.aiogram_fsm import CreatePlayerForm


class GetNewPlayerName(TextView):
    state = lambda: CreatePlayerForm.set_name

    @classmethod
    async def execute(cls, m: Message, state: FSMContext = None, **kwargs):
        if len(m.text) > 50:
            await m.answer('Имя должно быть меньше пятидесяти символов')
            return
        for entity in m.entities:
            if entity.type in ['mention', 'text_mention']:
                await m.answer('Имя не может содержать теги')
                return
        async with state.proxy() as dt:
            dt['name'] = m.html_text
        kb = ReplyKeyboardMarkup()
        male = KeyboardButton('Мужской')
        female = KeyboardButton('Женский')
        transgender = KeyboardButton('Трансгендер')
        kb.add(male, female, transgender)
        await m.answer('Какого ты пола?', reply_markup=kb)
        await CreatePlayerForm.next()
