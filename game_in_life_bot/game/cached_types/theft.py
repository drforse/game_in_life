from typing import Optional
from datetime import datetime

from pydantic import Field, PrivateAttr

from .base import GameInLifeCachedBaseObject
from ..types import Player
from ...redis_models import Theft as TheftModel


class Theft(GameInLifeCachedBaseObject):
    _model_type = PrivateAttr(TheftModel)
    _criminal: Optional[Player] = PrivateAttr(None)
    _victim: Optional[Player] = PrivateAttr(None)

    chat_id: int
    criminal_id: int
    victim_id: int
    stolen_money: float = 0.0
    stolen_items: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    success: bool = True
    is_completed: bool = False

    def get_criminal(self):
        if not self._criminal or self._criminal.tg_id != self.criminal_id:
            self._criminal = Player(tg_id=self.criminal_id)
        return self._criminal

    def get_victim(self):
        if not self._victim or self._victim.tg_id != self.victim_id:
            self._victim = Player(tg_id=self.victim_id)
        return self._victim
