from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
import re

from ...core import Command
from ...game import Game
from game.types import Player


class BaseAction(Command):
    custom_action_pattern = r'/action(@[^ \|]+)? [^\|]+(\|[^\|]+\| *([1-9][0-9]*|0) *)+ *\|[^\|]+$'

    @classmethod
    async def base_execute(cls, m: Message):
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
            async with cls.dp.current_state(chat=m.chat.id, user=m.from_user.id).proxy() as dt:
                dt['action'] = action
                print(m.text.split('|', maxsplit=1)[1].strip())
                dt['messages_and_delays'] = m.text.split('|', maxsplit=1)[1].strip()

        player = Player(tg_id=m.from_user.id)
        if m.from_user.id != m.reply_to_message.from_user.id:
            second_player = Player(tg_id=m.reply_to_message.from_user.id)
        else:
            await cls.accept_action(data=f'action {action_type} accept {player.tg_id} {player.tg_id}', message=m)
            return

        kb = InlineKeyboardMarkup()
        accept = InlineKeyboardButton('Го', callback_data=f'action {action_type} accept {player.tg_id} {second_player.tg_id}')
        decline = InlineKeyboardButton('Нее', callback_data=f'action {action_type} decline {player.tg_id} {second_player.tg_id}')
        kb.add(accept, decline)

        await m.answer('<a href="tg://user?id=%d">%s</a>, <a href="tg://user?id=%d">%s</a> предлагает %s'
                       % (second_player.tg_id, second_player.name, player.tg_id, player.name, action),
                       reply_markup=kb)

    @classmethod
    async def accept_action(cls, c: CallbackQuery = None, data: str = None, message: Message = None):
        if c:
            data = c.data

        data = data.split()
        user = int(data[-2])
        second_user = int(data[-1])
        action = data[1]
        player = Player(tg_id=user)
        second_player = Player(tg_id=second_user) if user != second_user else player

        msg = message or c.message

        async with cls.dp.current_state(chat=msg.chat.id, user=user).proxy() as dt:
            custom_data = dt or {}

        try:
            await msg.delete()
        except:
            pass
        await Game.process_accepted_action(action, cls.dp, cls.bot, msg.chat.id, player, second_player, custom_data)

    @classmethod
    async def decline_action(cls, c: CallbackQuery):
        data = c.data.split()
        user = int(data[-2])
        second_user = int(data[-1])
        action = data[1]
        player = Player(tg_id=user)
        second_player = Player(tg_id=second_user)

        async with cls.dp.current_state(chat=c.message.chat.id, user=user).proxy() as dt:
            custom_data = dt or {}

        await Game.process_declined_action(action, c, player, second_player, custom_data)
