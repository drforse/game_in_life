import re

from aiogram import Dispatcher
from aiogram_oop_framework.views import CallbackQueryView
from aiogram.types import CallbackQuery

from ...aiogram_fsm import ActionForm
from ....game.actions.actions_factory import ActionsFactory
from ....game.types.player import Player
from ...game import Game


class AcceptAction(CallbackQueryView):
    custom_filters = [lambda c: re.match('action .* accept ', c.data)]

    @classmethod
    async def execute(cls, c: CallbackQuery, state=None, **kwargs):
        data = c.data.split()
        user = int(data[-2])
        second_user = int(data[-1])
        action_type = data[1]
        player = Player(tg_id=user)
        second_player = Player(tg_id=second_user) if user != second_user else player

        dp = Dispatcher.get_current()
        for user in {user, second_user}:
            player = Player(tg_id=user)
            state = await dp.current_state(chat=c.message.chat.id, user=user).get_state()
            if state == ActionForm.busy.state:
                await c.answer("%s занят." % player.name, show_alert=True)
                return
        async with dp.current_state(chat=c.message.chat.id, user=user).proxy() as dt:
            action = dt.get('action')
        if not action:
            Action = ActionsFactory.get(action_type)
            action = Action(5, player, second_player, c.message.chat.id)

        try:
            await c.message.delete()
        except:
            pass
        await Game.process_accepted_action(action, dp, c.message.chat.id, player, second_player)
