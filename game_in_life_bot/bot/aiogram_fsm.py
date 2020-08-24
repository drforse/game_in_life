from aiogram.dispatcher.filters.state import State, StatesGroup


class CreateCountryForm(StatesGroup):
    set_name = State()


class CreatePlayerForm(StatesGroup):
    set_name = State()
    set_gender = State()
    set_pic = State()


class FuckForm(StatesGroup):
    fucking = State()
    masturbate = State()
