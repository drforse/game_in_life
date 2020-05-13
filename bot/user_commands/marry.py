from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from ..core import Command
from game.types import *


class Marry(Command):

    @staticmethod
    async def execute(m: Message):
        player = Player(tg_id=m.from_user.id)
        partner_player = Player(tg_id=m.reply_to_message.from_user.id)

        can_marry = await player.can_marry(m.chat.id, partner_player)

        if not can_marry['result']:
            await m.answer(player.cant_marry_reason_exaplanation[can_marry['reason']])
            return

        kb = InlineKeyboardMarkup()
        accept = InlineKeyboardButton('Принять', callback_data=f'marriage accept {player.tg_id} {partner_player.tg_id}')
        decline = InlineKeyboardButton('Отклонить',
                                       callback_data=f'marriage decline {player.tg_id} {partner_player.tg_id}')
        kb.add(accept, decline)

        await m.answer('<a href="tg://user?id=%d">%s</a>, <a href="tg://user?id=%d">%s</a> предлагает тебе свои руку '
                       'и сердце' % (partner_player.tg_id, partner_player.name, player.tg_id, player.name),
                       reply_markup=kb)

    @staticmethod
    async def accept_marriage(c: CallbackQuery):
        user = int(c.data.split()[-2])
        second_user = int(c.data.split()[-1])

        player = Player(tg_id=second_user)
        output = await player.marry(chat_tg_id=c.message.chat.id, partner_tg_id=user)
        await c.message.edit_text(output, reply_markup=None)

    @staticmethod
    async def decline_marriage(c: CallbackQuery):
        user = int(c.data.split()[-2])
        second_user = int(c.data.split()[-1])

        player = Player(tg_id=user)
        second_player = Player(tg_id=second_user)
        await c.answer('А жаль...')
        verb_form = ('отказала' if second_player.gender == 'male' else 'отказал'
                                if second_player.gender == 'female' else 'отказал(а)')
        await c.message.edit_text('<a href="tg://user?id=%d">%s</a> %s <a href="tg://user?id=%d">%s</a>' %
                                  (second_user, second_player.name, verb_form, user, player.name),
                                  reply_markup=None)
