from aiogram.types import Message
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from ..core import Command
from ..game import Game
from game.types import Player, Country
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
        country = Country(chat_tg_id=m.chat.id)
        if not country.exists:
            await m.answer('Привет. Придумайте название своей стране и напишите реплаем на это сообщение '
                           '(пока не придумаете, я тут писать не буду)')
            await cls.states_group.set_name.set()
            return

        user = User.get(tg_id=m.from_user.id, age__gte=0, age__lte=100)
        if not user:
            await m.answer('Привет, незнакомец. Ты в стране %s. Напиши мне в лс, чтобы играть.' % country.name)
            return
        if m.chat.id not in user.chats:
            user.update(push__chats=m.chat.id)
        await m.answer('Привет, %s. Ты находишься в стране %s' % (user.name, country.name))

    @classmethod
    async def execute_in_private(cls, m: Message):
        player = Player(tg_id=m.from_user.id)
        if not player.exists:
            await Game.process_new_user(m)
            return

        if not player.parents:
            await m.answer('Ждите своего рождения')
            return

        parent = Player(model_id=player.parents[0]).name if player.parents[0] != '0' else 'Ева'
        second_parent = Player(model_id=player.parents[1]).name if player.parents[1] != '0' else 'Адам'
        await m.answer('Имя: %s\nПол: %s\nВозраст: %s\nРодители: %s, %s\n' %
                       (player.name, player.gender, player.age, parent, second_parent))

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

        country = await Country(chat_tg_id=m.chat.id).create(name=m.html_text)
        await m.answer('Страна с названием %s успешно основана.' % country.name)
        await state.finish()
