from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram import Bot, Dispatcher
import logging
import typing
import random
import asyncio

from models import *
from game.types import Player
from config import SEX_DELAY_INTERVAL


class CreatePlayerForm(StatesGroup):
    set_name = State()
    set_gender = State()


class FuckForm(StatesGroup):
    fucking = State()
    masturbate = State()


class Game:

    @staticmethod
    async def process_new_user(m: Message):
        await m.answer('Привет. Мы с тобой незнакомы. Как тебя зовут?')
        await CreatePlayerForm.set_name.set()

    @staticmethod
    async def process_rebornig_user(m: Message):
        await m.answer('Привет. Ну что, по новой? Как тебя зовут?')
        await CreatePlayerForm.set_name.set()

    @staticmethod
    async def get_new_player_name(m: Message, state: FSMContext):
        if len(m.text) > 50:
            await m.answer('Имя должно быть меньше пятидесяти символов')
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

    @classmethod
    async def get_new_player_gender(cls, m: Message, state: FSMContext):
        gender = m.text.lower()
        if gender not in ('мужской', 'женский', 'трансгендер'):
            await m.answer('Выберите из предложенных вариантов!')
            return
        async with state.proxy() as dt:
            name = dt['name']
        gender_reference = {'мужской': 'male', 'женский': 'female', 'трансгендер': 'transgender'}

        old_user = User.get(tg_id=m.from_user.id)
        chats = old_user.chats if old_user else []

        user = User(tg_id=m.from_user.id, name=name, age=-1, gender=gender_reference[gender], chats=chats)
        user.save()
        text = 'Создан игрок с данными:\nИмя: %s\nПол: %s\nВозраст: 0\n' % (user.name, user.gender)
        if not await cls.get_users_availiable_for_children(user):
            text += 'Родители: Ева, Адам\n'
            user.parents = ['0', '0']
            user.age = 0
            user.save()
        else:
            user.save()
            text += ('\nЖдите своего рождения. Чтобы родиться, Вы должны написать /start хотя бы в одной из групп с '
                     'ботом (чем больше групп, тем выше скорость рождения).')
        await m.answer(text, reply_markup=ReplyKeyboardRemove())
        await state.finish()

    @staticmethod
    async def get_users_availiable_for_children(user: User):
        chats = user.chats
        result = []
        for chat in chats:
            females_in_marriage = []
            males_in_marriage = []
            users_in_marriage = User.objects(__raw__={f'partners.{chat}': {'$exists': True},
                                                      'age': {'$lte': 0, '$gte': 100}})
            print('users_in_marriage', [u.tg_id for u in users_in_marriage])
            for u in users_in_marriage:
                if u.gender == 'female':
                    females_in_marriage.append(u)
                elif u.gender == 'male':
                    males_in_marriage.append(u)
            females = []
            males = []
            for user in User.objects(chats=chat, age__gte=12, age__lte=100):
                if user.gender == 'female' and user not in females_in_marriage:
                    females.append(user)
                elif user.gender == 'male' and user not in males_in_marriage:
                    males.append(user)

            result += users_in_marriage  # + users_dating

            if len(females) > len(males):
                females = females[:len(males)]
            else:
                males = males[:len(females)]

            result += females + males

        print('result', [u.tg_id for u in result])
        return result

    @staticmethod
    async def process_died_user(bot: Bot, player: typing.Union[int, User, Player]):
        if isinstance(player, int):
            player = Player(tg_id=player)
        elif isinstance(player, User):
            player = Player(model=player)
        output = await player.die()
        for msg in output:
            try:
                await bot.send_message(msg, output[msg])
            except:
                pass

    @classmethod
    async def process_accepted_action(cls, action: str, dp: Dispatcher, bot: Bot,
                                      chat_tg_id: int, user: Player, second_user: Player, custom_data):
        for u in [user, second_user]:
            current_state = dp.current_state(chat=chat_tg_id, user=u.tg_id)
            await current_state.set_state(FuckForm.fucking)
            if second_user == user:
                break
        me = f'<a href="tg://user?id={user.tg_id}">{user.name}</a>'
        reply = f'<a href="tg://user?id={second_user.tg_id}">{second_user.name}</a>'
        output = await user.action(action, chat_tg_id, second_user,
                                   delay=random.randint(SEX_DELAY_INTERVAL[0],
                                                        SEX_DELAY_INTERVAL[1]),
                                   custom_data=custom_data.get('messages_and_delays'),
                                   me=me, reply=reply)
        async for out in output:
            if out['content_type'] == 'animation':
                try:
                    await bot.send_animation(chat_tg_id, out['content'])
                except:
                    pass
            elif out['content_type'] == 'text':
                try:
                    await bot.send_message(chat_tg_id, out['content'])
                except:
                    pass
            elif out['content_type'] == 'error' and out['content'] == 'NoCustomMessagesGiven':
                try:
                    await bot.send_message(chat_tg_id,
                                           'Кастомные сообщения не были даны или предложение устарело')
                except:
                    pass
            else:
                raise ContentTypeUnexpected(out['content_type'])
        for u in [user, second_user]:
            await dp.current_state(chat=chat_tg_id, user=u.tg_id).finish()
            if second_user == user:
                break

    @classmethod
    async def process_declined_action(cls, action: str, callback_query,
                                      player: Player, second_player: Player, custom_data=None):
        callback_answer = ''
        edit_text = ''
        verb_form = ('отказал' if second_player.gender == 'male' else 'отказала'
                               if second_player.gender == 'female' else 'отказал(а)')
        if action == 'fuck':
            callback_answer = 'Блин, а я уже камеру приготовил (9(('
            edit_text = '<a href="tg://user?id=%d">%s</a> не хочет ебаться с <a href="tg://user?id=%d">%s</a>'
        elif action == 'marriage':
            callback_answer = 'А жаль...'
            edit_text = ('<a href="tg://user?id=%d">%s</a> {} в браке '
                         '<a href="tg://user?id=%d">%s</a>'.format(verb_form))
        elif action == 'dating':
            callback_answer = 'А жаль...'
            edit_text = ('<a href="tg://user?id=%d">%s</a> {} в романтических '
                         'отношениях <a href="tg://user?id=%d">%s</a>'.format(verb_form))
        elif action == 'custom' and custom_data:
            edit_text = ('<a href="tg://user?id=%d">%s</a> не хочет {} с '
                         '<a href="tg://user?id=%d">%s</a>'.format(custom_data['action']))
        elif action == 'custom':
            edit_text = 'Кастомные сообщения не были даны или предложение устарело'
            await callback_query.message.edit_text(edit_text, reply_markup=None)
            return

        edit_text = edit_text % (second_player.tg_id, second_player.name, player.tg_id, player.name)
        await callback_query.answer(callback_answer)
        await callback_query.message.edit_text(edit_text, reply_markup=None)


class CountryDoesntExistException(Exception):
    def __init__(self, txt):
        self.txt = txt


class ContentTypeUnexpected(Exception):
    def __init__(self, txt):
        self.txt = txt
