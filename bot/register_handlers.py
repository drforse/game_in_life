from .game import Game, CreatePlayerForm
from .user_commands import *
from .core import Command


def register_handlers():
    Start.register(commands=['start'])
    Start.register(callback=Start.set_country_name, state=Start.states_group.set_name)

    Command.register(callback=Game.get_new_player_name, state=CreatePlayerForm.set_name)
    Command.register(callback=Game.get_new_player_gender, state=CreatePlayerForm.set_gender)

    Marry.register(commands=['marry'])
    Marry.reg_callback(Marry.accept_marriage, lambda c: c.data.startswith('marriage accept '))
    Marry.reg_callback(Marry.decline_marriage, lambda c: c.data.startswith('marriage decline '))

    Fuck.register(commands=['fuck'])
    Fuck.reg_callback(Fuck.accept_fuck, lambda c: c.data.startswith('fuck accept '))
    Fuck.reg_callback(Fuck.decline_fuck, lambda c: c.data.startswith('fuck decline '))

    Suicide.register(commands=['suicide'])
