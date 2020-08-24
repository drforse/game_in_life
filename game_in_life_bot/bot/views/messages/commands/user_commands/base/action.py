from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
import re

from .......bot.views.base import UserCommandView
from .......bot.views.callbacks.accept_action import AcceptAction
from .......game.types.player import Player
from ....... import config


class BaseAction(UserCommandView):
    custom_action_pattern = r'/action(@[^ \|]+)? [^\|]+(\|[^\|]+\| *([1-9][0-9]*|0) *)+ *\|[^\|]+$'

    @classmethod
    async def execute(cls, m: Message):
        try:
            await m.delete()
        except:
            pass

        if 'xbet' in m.text.lower():
            await m.answer('Идите нахуй со своим 1xbet, забаню щас блять')
            return

        action = m.text.split('|')[0].split(maxsplit=1)[1].strip()
        action_type = 'custom'
        if 'type:' in action:
            action_type = action.split('type:')[1].split()[0]
            action = action.replace(f'type:{action_type} ', '')
        if re.match(cls.custom_action_pattern, m.text):
            async with config.dp.current_state(chat=m.chat.id, user=m.from_user.id).proxy() as dt:
                dt['action'] = action
                dt['messages_and_delays'] = m.text.split('|', maxsplit=1)[1].strip()

        player = Player(tg_id=m.from_user.id)
        if m.from_user.id != m.reply_to_message.from_user.id:
            second_player = Player(tg_id=m.reply_to_message.from_user.id)
        else:
            await AcceptAction.execute(data=f'action {action_type} accept {player.tg_id} {player.tg_id}', message=m)
            return

        kb = InlineKeyboardMarkup()
        accept = InlineKeyboardButton('Го', callback_data=f'action {action_type} accept {player.tg_id} {second_player.tg_id}')
        decline = InlineKeyboardButton('Нее', callback_data=f'action {action_type} decline {player.tg_id} {second_player.tg_id}')
        kb.add(accept, decline)

        await m.answer('<a href="tg://user?id=%d">%s</a>, <a href="tg://user?id=%d">%s</a> предлагает %s'
                       % (second_player.tg_id, second_player.name, player.tg_id, player.name, action),
                       reply_markup=kb)
