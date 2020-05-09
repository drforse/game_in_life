from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from ..core import Command
from ..game import Game
from models import *


class Fuck(Command):

    @classmethod
    async def execute(cls, m: Message):

        user = User.objects(tg_id=m.from_user.id, age__gte=0, age__lte=100)
        if not user:
            await m.answer('Вы не играете. Чтобы начать напишите мне /start в лс')
            return

        if m.reply_to_message:
            second_user = User.objects(tg_id=m.reply_to_message.from_user.id, age__gte=0, age__lte=100)
            if not second_user:
                await m.answer('Пользователь не играет.')
                return
        else:
            second_user = user

        user = user[0]
        second_user = second_user[0]
        current_state = await (cls.dp.current_state(chat=m.chat.id, user=m.from_user.id)).get_state()
        if current_state:
            await m.answer('Вообще-то сейчас ты занят делом :3')

        kb = InlineKeyboardMarkup()
        accept = InlineKeyboardButton('Секс', callback_data=f'fuck accept {user.tg_id} {second_user.tg_id}')
        decline = InlineKeyboardButton('Нах', callback_data=f'fuck decline {user.tg_id} {second_user.tg_id}')
        kb.add(accept, decline)

        await m.answer('<a href="tg://user?id=%d">%s</a>, <a href="tg://user?id=%d">%s</a> предлагает поебаться'
                       % (second_user.tg_id, second_user.name, user.tg_id, user.name), reply_markup=kb)

    @classmethod
    async def accept_fuck(cls, c: CallbackQuery):
        user = int(c.data.split()[-2])
        second_user = int(c.data.split()[-1])
        if c.from_user.id != second_user:
            await c.answer('Это не ваше меню', show_alert=True)
            return
        user = User.objects(tg_id=user, age__gte=0, age__lte=100)[0]
        second_user = User.objects(tg_id=second_user, age__gte=0, age__lte=100)[0]

        await c.message.delete()
        await Game.process_fuck(cls.dp, c.message, user, second_user)

    @staticmethod
    async def decline_fuck(c: CallbackQuery):
        user = int(c.data.split()[-2])
        second_user = int(c.data.split()[-1])
        if c.from_user.id != second_user:
            await c.answer('Это не ваше меню', show_alert=True)
            return
        user = User.objects(tg_id=user, age__gte=0, age__lte=100)[0]
        second_user = User.objects(tg_id=second_user, age__gte=0, age__lte=100)[0]
        await c.answer('Блин, а я уе камеру приготовил (9((')
        await c.message.edit_text(
            '<a href="tg://user?id=%d">%s</a> не хочет ебаться с <a href="tg://user?id=%d">%s</a>' %
            (second_user.tg_id, second_user.name, user.tg_id, user.name),
            reply_markup=None)
