from aiogram.types import Message, CallbackQuery

from ...core import Command
from ...game import Game
from game.types import Player


class BaseAction(Command):

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

        if action == 'custom':
            async with cls.dp.current_state(chat=msg.chat.id, user=user).proxy() as dt:
                custom_data = dt

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
        custom_data = None
        if action == 'custom':
            async with cls.dp.current_state(chat=c.message.chat.id, user=user).proxy() as dt:
                custom_data = dt

        await Game.process_declined_action(action, c, player, second_player, custom_data)
