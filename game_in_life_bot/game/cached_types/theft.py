from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from bson import ObjectId
from pydantic import Field, PrivateAttr

from .base import GameInLifeCachedBaseObject
from ..types import Player
from ...config import THEFT_CATCHER_REWARD_MULTIPLIER, THEFT_FINE_MULTIPLIER
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

    @classmethod
    def get_last_from_player(cls, player_id: int) -> 'Theft':
        """
        returns the last theft by the player from database query sorted by creation time
        :param player_id:
        :return:
        """
        model = TheftModel.query.filter(
            criminal_id=player_id
        ).order_by("-created_at").first()
        return cls.from_db(model)

    @classmethod
    def get_last_with_players_in_chat(cls, criminal_id: int, victim_id: int, chat_id: int) -> 'Theft':
        """
        returns the last theft with given filters from database query sorted by creation time
        :param criminal_id:
        :param victim_id:
        :param chat_id:
        :return:
        """
        model = TheftModel.query.filter(
            criminal_id=criminal_id, victim_id=victim_id, chat_id=chat_id
        ).order_by("-created_at").first()
        return cls.from_db(model)

    def complete(self, set_success: Optional[bool] = None):
        if set_success is not None:
            self.success = set_success
        self.is_completed = True
        self.save_to_db()

    def process_catch(self, catcher: Player) -> 'Catch':
        self.complete(set_success=False)

        criminal = Player(tg_id=self.criminal_id)
        victim = Player(tg_id=self.victim_id)
        fine = self.stolen_money * THEFT_FINE_MULTIPLIER
        catcher_reward = self.stolen_money * THEFT_CATCHER_REWARD_MULTIPLIER
        await criminal.balance.add_money_to_main_currency_balance(-(self.stolen_money + fine))
        await victim.balance.add_money_to_main_currency_balance(self.stolen_money)
        for item_id, quantity in self.stolen_items.items():
            criminal.backpack[item_id] -= quantity
            victim.backpack[item_id] += quantity
        await criminal.save_to_db()
        await victim.save_to_db()

        await catcher.balance.add_money_to_main_currency_balance(fine)
        return Catch(fine=fine, catcher_reward=catcher_reward)


@dataclass
class Catch:
    fine: float
    catcher_reward: float
