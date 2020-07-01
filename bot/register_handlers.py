import re

from .game import Game, CreatePlayerForm
from .user_commands import *
from .dev_commands import *
from .core import Command
from .user_commands.base.action import BaseAction


def register_handlers():
    Start.register()
    Start.register(callback=Start.set_country_name, state=Start.states_group.set_name, set_commands=False)

    Command.register(callback=Game.get_new_player_name, state=CreatePlayerForm.set_name, set_commands=False)
    Command.register(callback=Game.get_new_player_gender, state=CreatePlayerForm.set_gender, set_commands=False)

    BaseAction.reg_callback(BaseAction.accept_action, lambda c: re.match('action .* accept ', c.data))
    BaseAction.reg_callback(BaseAction.decline_action, lambda c: re.match('action .* decline ', c.data))

    Action.register()

    Marry.register()

    Fuck.register()

    Suicide.register()

    Divorce.register()

    Me.register(state='*')

    You.register(state='*')

    Date.register()

    Breakup.register()

    AddSexGif.register()

    AddCumSexGif.register()

    DelSexGif.register()

    DelCumSexGif.register()

    Restart.register()
