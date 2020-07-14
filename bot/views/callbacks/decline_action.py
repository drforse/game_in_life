import re

from aiogram_oop_framework.views import CallbackQueryView
from aiogram.types import CallbackQuery, Message

from game.types.player import Player
from ...game import Game
import config


class AcceptAction(CallbackQueryView):
    custom_filters = [lambda c: re.match('action .* decline ', c.data)]

    @classmethod
    async def execute(cls, c: CallbackQuery = None):
        data = c.data.split()
        user = int(data[-2])
        second_user = int(data[-1])
        action = data[1]
        player = Player(tg_id=user)
        second_player = Player(tg_id=second_user)

        async with config.dp.current_state(chat=c.message.chat.id, user=user).proxy() as dt:
            custom_data = dt or {}

        await Game.process_declined_action(action, c, player, second_player, custom_data)
