from aiogram.types import Message
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from ..core import Command
from ..game import Game
from models import *


class CreateCountryForm(StatesGroup):
    set_name = State()


class Start(Command):
    states_group = CreateCountryForm

    @classmethod
    async def execute(cls, m: Message):
        if m.chat.type == 'private':
            await cls.execute_in_private(m)
            return
        country = Country.objects(chat_tg_id=m.chat.id)
        if not country:
            await m.answer('Привет. Придумайте название своей стране и напишите реплаем на это сообщение '
                           '(пока не придумаете, я тут писать не буду)')
            await cls.states_group.set_name.set()
            return

        country = country[0]
        user = User.objects(tg_id=m.from_user.id, age__gte=0, age__lte=100)
        if not user:
            await m.answer('Привет, незнакомец. Ты в стране %s. Напиши мне в лс, чтобы играть.' % country.name)
            return
        user = user[0]
        if m.chat.id not in user.chats:
            user.update(push__chats=m.chat.id)
        await m.answer('Привет, %s. Ты находишься в стране %s' % (user.name, country.name))

    @classmethod
    async def execute_in_private(cls, m: Message):
        user = User.objects(tg_id=m.from_user.id, age__gte=0, age__lte=100)
        if not user:
            await Game.process_new_user(m)
            return
        user = user[0]
        await m.answer('Привет, %s' % user.name)
        await Game.get_available_pairs(user)

    @classmethod
    async def set_country_name(cls, m: Message, state: FSMContext):
        if not m.reply_to_message:
            return
        member = await m.chat.get_member(m.reply_to_message.from_user.id)
        if member.status not in ['administrator', 'creator']:
            await m.answer('Название страны может задавать только админ группы')
            return
        if len(m.text) > 50:
            await m.answer('Название должно быть не длиннее пятидесяти символов.')
            return

        Country(chat_tg_id=m.chat.id, name=m.text).save()
        await m.answer('Страна с названием %s успешно основана.' % m.text)
        await state.finish()
