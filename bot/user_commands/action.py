from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import re

from .base.action import BaseAction
from game.types import Player


class Action(BaseAction):

    @classmethod
    async def execute(cls, m: Message):
        if not re.match(r'/action(@.+)? .+ (\| .+ \| [1-9][0-9]*)+ \| .+$', m.text):
            await m.answer('Команда не следует шаблону "/action действие | сообщение | ожидание | сообщение..."\n'
                           'Пример: /action сходить в кафе | {me} и {reply} пошли в кафе | 5 | {me} и {reply} пьют '
                           'кофе | 0 | {me} обняла {reply} и они разошлись по домам')
            return

        try:
            await m.delete()
        except:
            pass

        action = m.text.split('|')[0].split(maxsplit=1)[1].strip()
        async with cls.dp.current_state(chat=m.chat.id, user=m.from_user.id).proxy() as dt:
            dt['action'] = action
            print(m.text.split('|', maxsplit=1)[1].strip())
            dt['messages_and_delays'] = m.text.split('|', maxsplit=1)[1].strip()

        player = Player(tg_id=m.from_user.id)
        if m.from_user.id != m.reply_to_message.from_user.id:
            second_player = Player(tg_id=m.reply_to_message.from_user.id)
        else:
            await cls.accept_action(data=f'action custom accept {player.tg_id} {player.tg_id}', message=m)
            return

        kb = InlineKeyboardMarkup()
        accept = InlineKeyboardButton('Го', callback_data=f'action custom accept {player.tg_id} {second_player.tg_id}')
        decline = InlineKeyboardButton('Нее', callback_data=f'action custom decline {player.tg_id} {second_player.tg_id}')
        kb.add(accept, decline)

        await m.answer('<a href="tg://user?id=%d">%s</a>, <a href="tg://user?id=%d">%s</a> предлагает %s'
                       % (second_player.tg_id, second_player.name, player.tg_id, player.name, action),
                       reply_markup=kb)
