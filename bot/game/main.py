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


class FuckForm(StatesGroup):
    fucking = State()
    masturbate = State()


class CreatePlayerForm(StatesGroup):
    set_name = State()
    set_gender = State()


class Game:

    @staticmethod
    async def process_new_user(m: Message):
        await m.answer('Привет. Мы с тобой незнакомы. Как тебя зовут?')
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

        user = User(tg_id=m.from_user.id, name=name, age=-1, gender=gender_reference[gender], chats=chats).save()
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
                                             'age': {'$gte': 12, '$lte': 100}})
            print('users_in_marriage', [u.tg_id for u in users_in_marriage])
            for u in users_in_marriage:
                if u.gender == 'females':
                    females_in_marriage.append(u)
                elif u.gender == 'males':
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
    async def process_died_user(bot: Bot, user: typing.Union[int, User]):
        if isinstance(user, int):
            player = Player(tg_id=user)
        else:
            player = Player(model=user)
        output = await player.die()
        for msg in output:
            await bot.send_message(msg, output[msg])

    @classmethod
    async def process_fuck(cls, dp: Dispatcher, m: Message, user: Player, second_user: Player):
        if user.tg_id == second_user.tg_id:
            start_message = '<a href="tg://user?id=%d">%s</a> дрочит.' % (user.tg_id, user.name)
            current_state = dp.current_state(chat=m.chat.id, user=user.tg_id)
            await current_state.set_state(FuckForm.masturbate)
            end_message = '<a href="tg://user?id=%d">%s</a> кончил.' % (user.tg_id, user.name)
        else:
            start_message = '<a href="tg://user?id=%d">%s</a> и <a href="tg://user?id=%d">%s</a> пошли трахаться :3' %\
                            (user.tg_id, user.name, second_user.tg_id, second_user.name)
            for u in [user, second_user]:
                current_state = dp.current_state(chat=m.chat.id, user=u.tg_id)
                await current_state.set_state(FuckForm.fucking)
            end_message = '<a href="tg://user?id=%d">%s</a> и <a href="tg://user?id=%d">%s</a> закончили трахаться' % \
                          (user.tg_id, user.name, second_user.tg_id, second_user.name)

            child = None
            female = user if user.gender == 'female' else second_user if second_user.gender == 'female' else None
            male = user if user.gender == 'male' else second_user if second_user.gender == 'male' else None
            if male and female and female.age >= 12:

                childs_queue = await cls.get_childs_queue(chat=m.chat.id)
                if childs_queue:
                    child = random.choice(childs_queue)

            if child:
                mother = user if user.gender == 'female' else second_user
                father = user if user.gender == 'male' else second_user
                end_message += ('\n\n<a href="tg://user?id=%d">%s</a> забеременела и родила '
                                '<a href="tg://user?id=%d">%s</a>' % (mother.tg_id, mother.name, child.tg_id,
                                                                      child.name)
                                )
                await cls.born_child(mother, father, child, m.chat.id)

        await m.answer(start_message)
        await asyncio.sleep(random.randint(10, 120))
        await m.answer(end_message)
        for u in [user, second_user]:
            await dp.current_state(chat=m.chat.id, user=u.tg_id).finish()

    @staticmethod
    async def born_child(mother: Player, father: Player, child: User, chat: typing.Union[Group, int]):
        if isinstance(chat, Group):
            chat = Group.chat_tg_id
        child.delete()
        child = User(tg_id=child.tg_id, name=child.name, gender=child.gender, age=0, chats=child.chats,
                     parents=[mother.pk, father.pk])
        child.save()
        mother.model.push_child(chat, child.pk)
        father.model.push_child(chat, child.pk)

    @staticmethod
    async def get_childs_queue(chat: typing.Union[Group, int]) -> typing.Optional[typing.Iterable[User]]:
        if isinstance(chat, Group):
            chat = chat.chat_tg_id
        return User.objects(age=-1, chats=chat)


class CountryDoesntExistException(Exception):
    def __init__(self, txt):
        self.txt = txt
