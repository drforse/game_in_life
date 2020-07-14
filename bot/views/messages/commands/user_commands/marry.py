from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from bot.views.base import UserCommandView
from game.types.player import *


class Marry(UserCommandView):
    needs_satiety_level = 35

    @staticmethod
    async def execute(m: Message):
        player = Player(tg_id=m.from_user.id)
        partner_player = Player(tg_id=m.reply_to_message.from_user.id)

        can_marry = await player.can_marry(m.chat.id, partner_player)

        if not can_marry['result']:
            await m.answer(player.cant_marry_reason_exaplanation[can_marry['reason']])
            return

        try:
            await m.delete()
        except:
            pass

        kb = InlineKeyboardMarkup()
        accept = InlineKeyboardButton('Принять', callback_data=f'action marriage accept {player.tg_id} {partner_player.tg_id}')
        decline = InlineKeyboardButton('Отклонить',
                                       callback_data=f'action marriage decline {player.tg_id} {partner_player.tg_id}')
        kb.add(accept, decline)

        await m.answer('<a href="tg://user?id=%d">%s</a>, <a href="tg://user?id=%d">%s</a> предлагает тебе свои руку '
                       'и сердце' % (partner_player.tg_id, partner_player.name, player.tg_id, player.name),
                       reply_markup=kb)
