from aiogram_oop_framework.views import TextView
from aiogram.types import Message
from aiogram.dispatcher import FSMContext

from .....game.types.player import Country
from .....bot.aiogram_fsm import CreateCountryForm


class SetCountryName(TextView):
    state = lambda: CreateCountryForm.set_name

    @classmethod
    async def execute(cls, m: Message, state: FSMContext = None, **kwargs):
        if not m.reply_to_message:
            return
        member = await m.chat.get_member(m.from_user.id)
        if member.status not in ['administrator', 'creator']:
            await m.answer('Название страны может задавать только админ группы')
            return
        if len(m.text) > 50:
            await m.answer('Название должно быть не длиннее пятидесяти символов.')
            return

        country = await Country(chat_tg_id=m.chat.id).create(name=m.html_text)
        await state.finish()
        await m.answer('Страна с названием %s успешно основана.' % country.name)

