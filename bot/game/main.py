from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from models import *


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
            dt['name'] = m.text
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

        user = User(tg_id=m.from_user.id, name=name, gender=gender_reference[gender]).save()
        text = 'Создан игрок с данными:\nИмя: %s\nПол: %s\nВозраст: %d\n' % (user.name, user.gender, user.age)
        if not cls.get_available_pairs(user):
            text += 'Мать: Ева\nОтец: Адам\n'
            user.parents = ['0', '0']
        else:
            text += ('\nЖдите своего рождения. Чтобы родиться, Вы должны написать /start хотя бы в одной из групп с '
                     'ботом (чем больше групп, тем выше скорость рождения).')
        await m.answer(text, reply_markup=ReplyKeyboardRemove())
        await state.finish()

    @staticmethod
    async def get_available_pairs(user: User):
        chats = user.chats
        pairs = []
        for chat in chats:
            pairs += User.objects(__raw__={f'partners.{chat}': {'$exists': True},
                                           'age': {'$gte': 0, '$lte': 100}})
        return pairs

    @staticmethod
    async def process_died_user(m: Message, user: User):
        childs_list = []
        for chat in user.partners:
            childs = user.childs.get(chat)
            childs_list.append(childs)
            partner_user = User.objects(pk=user.partners[chat], age__gte=0, age__lte=100)
            if not partner_user:
                continue
            partner_user = partner_user[0]
            country = Country.objects(chat_tg_id=chat)
            await m.bot.send_message(partner_user.tg_id, 'Ваш партнер в стране %s, %s - умер...' %
                                     (country.name, user.name))

        for child in childs_list:
            child_user = User.objects(pk=child, age__gte=0, age__lte=100)
            if not child_user:
                continue
            child_user = child_user[0]
            await m.bot.send_message(child_user.tg_id, 'Ваш родитель, %s - умер...' % user.name)

        for parent in user.parents:
            parent_user = User.objects(pk=parent, age__gte=0, age__lte=100)
            if not parent_user:
                continue
            parent_user = parent_user[0]
            await m.bot.send_message(parent_user.tg_id, 'Ваше чадо, %s - умерло...' % user.name)
