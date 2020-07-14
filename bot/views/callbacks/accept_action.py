import re

from aiogram_oop_framework.views import CallbackQueryView
from aiogram.types import CallbackQuery, Message

from game.types.player import Player
from ...game import Game
import config


class AcceptAction(CallbackQueryView):
    custom_filters = [lambda c: re.match('action .* accept ', c.data)]

    @classmethod
    async def execute(cls, c: CallbackQuery = None, data: str = None, message: Message = None):
        if c:
            data = c.data

        data = data.split()
        user = int(data[-2])
        second_user = int(data[-1])
        action = data[1]
        player = Player(tg_id=user)
        second_player = Player(tg_id=second_user) if user != second_user else player

        msg = message or c.message

        async with config.dp.current_state(chat=msg.chat.id, user=user).proxy() as dt:
            custom_data = dt or {}

        try:
            await msg.delete()
        except:
            pass
        await Game.process_accepted_action(action, config.dp, cls.bot, msg.chat.id, player, second_player, custom_data)
