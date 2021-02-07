from typing import Dict, List

from aiogram.utils import helper

from .base import GameInLifeDbBaseObject
from ...models import PerkModel


class Perk(GameInLifeDbBaseObject):
    model_type = PerkModel

    def __init__(self,
                 model: PerkModel = None,
                 **kwargs):
        self.title: str = ""
        self.limits: Dict[int, List[str]] = {}
        super().__init__(model, **kwargs)

    def to_db(self):
        return {'title': self.title,
                'limits': self.limits}


class Perks(helper.Helper):
    mode = 'snake_case'
    THEFT = helper.Item()
    ARREST = helper.Item()
