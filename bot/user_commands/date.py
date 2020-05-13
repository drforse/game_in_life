from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from ..core import Command
from game.types import *


class Date(Command):

    @staticmethod
    async def execute(m: Message):
        player = Player(tg_id=m.from_user.id)
        lover_player = Player(tg_id=m.reply_to_message.from_user.id)

        can_date = await player.can_date(m.chat.id, lover_player)

        if not can_date['result']:
            await m.answer(player.cant_date_reason_exaplanation[can_date['reason']])
            return

        kb = InlineKeyboardMarkup()
        accept = InlineKeyboardButton('Принять', callback_data=f'dating accept {player.tg_id} {lover_player.tg_id}')
        decline = InlineKeyboardButton('Отклонить',
                                       callback_data=f'dating decline {player.tg_id} {lover_player.tg_id}')
        kb.add(accept, decline)

        await m.answer('<a href="tg://user?id=%d">%s</a>, <a href="tg://user?id=%d">%s</a> предлагает тебе встречаться '
                       % (lover_player.tg_id, lover_player.name, player.tg_id, player.name),
                       reply_markup=kb)

    @staticmethod
    async def accept_dating(c: CallbackQuery):
        user = int(c.data.split()[-2])
        second_user = int(c.data.split()[-1])

        player = Player(tg_id=second_user)
        output = await player.date(chat_tg_id=c.message.chat.id, lover_tg_id=user)
        await c.message.edit_text(output, reply_markup=None)

    @staticmethod
    async def decline_dating(c: CallbackQuery):
        user = int(c.data.split()[-2])
        second_user = int(c.data.split()[-1])

        player = Player(tg_id=user)
        second_player = Player(tg_id=second_user)
        await c.answer('А жаль...')
        verb_form = ('отказала' if second_player.gender == 'male' else 'отказал'
                                if second_player.gender == 'female' else 'отказал(а)')
        await c.message.edit_text('<a href="tg://user?id=%d">%s</a> %s в романтических отношениях '
                                  '<a href="tg://user?id=%d">%s</a>' %
                                  (second_user, second_player.name, verb_form, user, player.name),
                                  reply_markup=None)
