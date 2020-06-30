import re

from .game import Game, CreatePlayerForm
from .user_commands import *
from .dev_commands import *
from .core import Command
from .user_commands.base.action import BaseAction


def register_handlers():
    Start.register(commands=['start'])
    Start.register(callback=Start.set_country_name, state=Start.states_group.set_name)

    Command.register(callback=Game.get_new_player_name, state=CreatePlayerForm.set_name)
    Command.register(callback=Game.get_new_player_gender, state=CreatePlayerForm.set_gender)

    BaseAction.reg_callback(BaseAction.accept_action, lambda c: re.match('action .* accept ', c.data))
    BaseAction.reg_callback(BaseAction.decline_action, lambda c: re.match('action .* decline ', c.data))

    Action.register(commands=['action'])

    Marry.register(commands=['marry'])

    Fuck.register(commands=['fuck'])

    Suicide.register(commands=['suicide'])

    Divorce.register(commands=['divorce'])

    Me.register(commands=['me'], state='*')

    You.register(commands=['you'], state='*')

    Date.register(commands=['date'])

    Breakup.register(commands=['breakup'])

    AddSexGif.register(commands=['addsexgif'])

    AddCumSexGif.register(commands=['addcumsexgif'])

    DelSexGif.register(commands=['delsexgif'])

    DelCumSexGif.register(commands=['delcumsexgif'])
