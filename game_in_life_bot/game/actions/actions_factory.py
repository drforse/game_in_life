from .action import Action
from .fuck import FuckAction
from .date import DateAction
from .marry import MarryAction
from .custom import CustomAction


class ActionsFactory:
    actions = {'fuck': FuckAction,
               'dating': DateAction,
               'marriage': MarryAction,
               'custom': CustomAction}

    @classmethod
    def add(cls, name: str, action: Action.__class__):
        cls.actions[name] = action

    @classmethod
    def get(cls, name: str):
        return cls.actions.get(name)
