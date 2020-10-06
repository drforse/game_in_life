import random

from aiogram import Dispatcher
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram_oop_framework.views import UserBaseView

from .......game.types.player import Player
from ......game import Game
from ....... import config
from .......game.actions.actions_factory import ActionsFactory


class BaseAction(UserBaseView):
    custom_action_pattern = r'/action(@[^ \|]+)? [^\|]+(\|[^\|]+\| *([1-9][0-9]*|0) *)+ *\|[^\|]+$'
    needs_satiety_level = 5

    @classmethod
    async def execute_action(cls, m: Message):
        try:
            await m.delete()
        except:
            pass

        if 'xbet' in m.text.lower():
            await m.answer('Идите нахуй со своим 1xbet, забаню щас блять')
            return

        action_split = m.text.split('|', maxsplit=1)
        description = action_split[0].split(maxsplit=1)[1].strip()
        action_type = 'custom'
        if 'type:' in description:
            action_type = description.split('type:')[1].split()[0]
            description = description.replace(f'type:{action_type} ', '')

        user = m.from_user
        second_user = m.reply_to_message.from_user

        player = Player(tg_id=user.id)
        second_player = Player(tg_id=second_user.id)

        Action = ActionsFactory.get(action_type)
        action = Action(cls.needs_satiety_level, player, second_player, m.chat.id)
        delay = random.randint(config.SEX_DELAY_INTERVAL[0], config.SEX_DELAY_INTERVAL[1])
        custom_data = action_split[1].strip() if len(action_split) > 1 else ""
        await action.complete(custom_data=custom_data, delay=delay)

        dp = Dispatcher.get_current()

        if user.id == second_user.id or not second_player.alive:
            await Game.process_accepted_action(action, dp, m.chat.id, player, second_player)
            return

        async with dp.current_state(chat=m.chat.id, user=m.from_user.id).proxy() as dt:
            dt['action'] = action

        kb = InlineKeyboardMarkup()
        accept = InlineKeyboardButton(
            'Го', callback_data=f'action {action_type} accept {player.tg_id} {second_player.tg_id}')
        decline = InlineKeyboardButton(
            'Нее', callback_data=f'action {action_type} decline {player.tg_id} {second_player.tg_id}')
        kb.add(accept, decline)

        await m.answer(
            '%s, %s предлагает %s' % (
                second_user.get_mention(
                    second_player.name), user.get_mention(player.name), description),
            reply_markup=kb)
