from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from ..core import Command
from game.types import *


class Marry(Command):

    @staticmethod
    async def execute(m: Message):
        if not m.reply_to_message:
            await m.answer('Команда должна быть реплаем.')
            return
        player = Player(tg_id=m.from_user.id)
        second_player = Player(tg_id=m.reply_to_message.from_user.id)
        if not player.exists:
            await m.answer('Вы не играете. Чтобы начать напишите мне /start в лс')
            return
        if not second_player.exists:
            await m.answer('Пользователь не играет.')
            return

        if player.tg_id == second_player.tg_id:
            await m.answer('Sry, but you can\'t marry yourself')
            return

        if player.age < 16 or second_player.age < 16:
            await m.answer('Вступать в брак можно только с 16-ти лет, до 16-ти можно только встречаться - /date')
            return

        kb = InlineKeyboardMarkup()
        accept = InlineKeyboardButton('Принять', callback_data=f'marriage accept {player.tg_id} {second_player.tg_id}')
        decline = InlineKeyboardButton('Отклонить',
                                       callback_data=f'marriage decline {player.tg_id} {second_player.tg_id}')
        kb.add(accept, decline)

        await m.answer('<a href="tg://user?id=%d">%s</a>, <a href="tg://user?id=%d">%s</a> предлагает тебе свои руку '
                       'и сердце' % (second_player.tg_id, second_player.name, player.tg_id, player.name),
                       reply_markup=kb)

    @staticmethod
    async def accept_marriage(c: CallbackQuery):
        user = int(c.data.split()[-2])
        second_user = int(c.data.split()[-1])
        if c.from_user.id != second_user:
            await c.answer('Это не ваше меню', show_alert=True)
            return
        player = Player(tg_id=user)
        output = await player.marry(chat_tg_id=c.message.chat.id, partner_tg_id=second_user)
        await c.message.edit_text(output, reply_markup=None)

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
        verb_form = ('отказала' if second_user.gender == 'male' else 'отказал'
                                if second_user.gender == 'female' else 'отказал(а)')
        await c.message.edit_text('<a href="tg://user?id=%d">%s</a> %s <a href="tg://user?id=%d">%s</a>' %
                                  (second_user.tg_id, second_user.name, verb_form, user.tg_id, user.name),
                                  reply_markup=None)
