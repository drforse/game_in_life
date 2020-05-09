from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from ..core import Command
from models import *


class Marry(Command):

    @staticmethod
    async def execute(m: Message):
        if not m.reply_to_message:
            await m.answer('Команда должна быть реплаем.')
            return
        user = User.objects(tg_id=m.from_user.id, age__gte=0, age__lte=100)
        second_user = User.objects(tg_id=m.reply_to_message.from_user.id, age__gte=0, age__lte=100)
        if not user:
            await m.answer('Вы не играете. Чтобы начать напишите мне /start в лс')
            return
        if not second_user:
            await m.answer('Пользователь не играет.')
            return

        user = user[0]
        second_user = second_user[0]
        if user.tg_id == second_user.tg_id:
            await m.answer('Sry, but you can\'t marry yourself')
            return

        if user.age < 16 or second_user.age < 16:
            await m.answer('Вступать в брак можно только с 16-ти лет, до 16-ти можно только встречаться - /date')
            return

        kb = InlineKeyboardMarkup()
        accept = InlineKeyboardButton('Принять', callback_data=f'marriage accept {m.from_user.id} {second_user.tg_id}')
        decline = InlineKeyboardButton('Отклонить',
                                       callback_data=f'marriage decline {m.from_user.id} {second_user.tg_id}')
        kb.add(accept, decline)

        await m.answer('<a href="tg://user?id=%d">%s</a>, <a href="tg://user?id=%d">%s</a> предлагает тебе свои руку '
                       'и сердце' % (second_user.tg_id, second_user.name, user.tg_id, user.name), reply_markup=kb)

    @staticmethod
    async def accept_marriage(c: CallbackQuery):
        user = int(c.data.split()[-2])
        second_user = int(c.data.split()[-1])
        if c.from_user.id != second_user:
            await c.answer('Это не ваше меню', show_alert=True)
            return
        user = User.objects(tg_id=user, age__gte=0, age__lte=100)[0]
        second_user = User.objects(tg_id=second_user, age__gte=0, age__lte=100)[0]
        if str(c.message.chat.id) in second_user.partners:
            await c.answer('Вы уже в браке в этой стране')
            await c.message.delete()
            return
        if str(c.message.chat.id) in user.partners:
            await c.answer('%s уже в браке' % user.name)
            await c.message.delete()
            return
        user.update(__raw__={'$set': {f'partners.{c.message.chat.id}': second_user.pk}})
        second_user.update(__raw__={'$set': {f'partners.{c.message.chat.id}': user.pk}})
        await c.message.delete()
        await c.message.answer('Поздавляем <a href="tg://user?id=%d">%s</a> и <a href="tg://user?id=%d">%s</a> со '
                               'свадьбой' % (user.tg_id, user.name, second_user.tg_id, second_user.name))

    @staticmethod
    async def decline_marriage(c: CallbackQuery):
        user = int(c.data.split()[-2])
        second_user = int(c.data.split()[-1])
        if c.from_user.id != second_user:
            await c.answer('Это не ваше меню', show_alert=True)
            return
        user = User.objects(tg_id=user, age__gte=0, age__lte=100)[0]
        second_user = User.objects(tg_id=second_user, age__gte=0, age__lte=100)[0]
        await c.answer('А жаль...')
        if second_user.gender == 'male':
            await c.message.edit_text('<a href="tg://user?id=%d">%s</a> отказал <a href="tg://user?id=%d">%s</a>' %
                                      (second_user.tg_id, second_user.name, user.tg_id, user.name),
                                      reply_markup=None)
        elif second_user.gender == 'female':
            await c.message.edit_text('<a href="tg://user?id=%d">%s</a> отказала <a href="tg://user?id=%d">%s</a>' %
                                      (second_user.tg_id, second_user.name, user.tg_id, user.name),
                                      reply_markup=None)
        else:
            await c.message.edit_text('<a href="tg://user?id=%d">%s</a> отказал(а) <a href="tg://user?id=%d">%s</a>' %
                                      (second_user.tg_id, second_user.name, user.tg_id, user.name),
                                      reply_markup=None)
