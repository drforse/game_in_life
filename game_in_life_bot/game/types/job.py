from typing import Dict, List

from aiogram.utils import helper

from .base import GameInLifeDbBaseObject
from .perk import Perk
from ...models import JobModel


class Job(GameInLifeDbBaseObject):
    model_type = JobModel

    def __init__(self,
                 model: JobModel = None,
                 **kwargs):
        self.title: str = ""
        self.new_perks_by_job_level: Dict[str, List[Perk]] = {}
        self.limits: Dict[str, Dict] = {}
        super().__init__(model, **kwargs)

    @staticmethod
    def _resolve_field_from_db(name, value):
        if name == 'new_perks_by_job_level':
            return {k: [Perk(id=perk) for perk in v] for k, v in value.items()}
        return value

    @staticmethod
    def _resolve_field_to_db(name, value):
        if name == 'new_perks_by_job_level':
            return [perk.to_db() for perk in value]
        return value


class Jobs(helper.Helper):
    mode = 'snake_case'
    POLICEMAN = helper.Item()
