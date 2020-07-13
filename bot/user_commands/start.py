from aiogram.types import Message
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from ..core import Command
from ..game import Game
from game.types.player import Player, Country
from .me import Me


class CreateCountryForm(StatesGroup):
    set_name = State()


class Start(Command):
    needs_auth = False
    needs_reply_auth = False
    needs_satiety_level = 0
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

        player = Player(tg_id=m.from_user.id)
        if not player.exists:
            await m.answer('Привет, незнакомец. Ты в стране %s. Напиши мне в лс, чтобы играть.' % country.name)
            return
        if not player.alive:
            await m.answer('Привет, мертвец. Ты в стране %s. Напиши мне в лс, чтобы ожить. '
                           'Мертвые не играют' % country.name)
            return
        await m.answer('Привет, %s. Ты находишься в стране %s' % (player.name, country.name))

    @classmethod
    async def execute_in_private(cls, m: Message):
        player = Player(tg_id=m.from_user.id)

        if not player.exists:
            await Game.process_new_user(m)
            return
        if not player.alive and not player.in_born_queue:
            await Game.process_rebornig_user(m)
            return

        await Me.execute_in_private(m, player)

    @classmethod
    async def set_country_name(cls, m: Message, state: FSMContext):
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
