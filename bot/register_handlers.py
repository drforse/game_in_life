from .game import Game, CreatePlayerForm
from .user_commands import Start
from .core import Command


def register_handlers():
    Start.register(commands=['start'])
    Start.register(callback=Start.set_country_name, state=Start.states_group.set_name)
    Command.register(callback=Game.get_new_player_name, state=CreatePlayerForm.set_name)
    Command.register(callback=Game.get_new_player_gender, state=CreatePlayerForm.set_gender)
