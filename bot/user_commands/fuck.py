from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from .base.action import BaseAction
from game.types import Player


class Fuck(BaseAction):

    @classmethod
    async def execute(cls, m: Message):

        player = Player(tg_id=m.from_user.id)
        if m.from_user.id != m.reply_to_message.from_user.id:
            second_player = Player(tg_id=m.reply_to_message.from_user.id)
        else:
            await cls.accept_action(data=f'action fuck accept {player.tg_id} {player.tg_id}', message=m)
            return

        kb = InlineKeyboardMarkup()
        accept = InlineKeyboardButton('Секс', callback_data=f'action fuck accept {player.tg_id} {second_player.tg_id}')
        decline = InlineKeyboardButton('Нах', callback_data=f'action fuck decline {player.tg_id} {second_player.tg_id}')
        kb.add(accept, decline)

        await m.answer('<a href="tg://user?id=%d">%s</a>, <a href="tg://user?id=%d">%s</a> предлагает поебаться'
                       % (second_player.tg_id, second_player.name, player.tg_id, player.name), reply_markup=kb)
