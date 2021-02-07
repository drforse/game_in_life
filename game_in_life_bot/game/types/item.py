from datetime import datetime

from .effect import Effect
from ...models import ItemModel
from .base import GameInLifeDbBaseObject
from ..exceptions import *


class Item(GameInLifeDbBaseObject):
    model_type = ItemModel

    def __init__(self,
                 model: ItemModel = None,
                 **kwargs):
        self.price: float = None
        self.emoji: str = None
        self.type: str = None
        self.name: str = None
        self.weight: float = None
        self.effects: list = None
        super().__init__(model, **kwargs)

    @staticmethod
    def _resolve_field_from_db(name, value):
        if name == 'effects':
            return [Effect(**e) for e in value]
        return value

    @staticmethod
    def _resolve_field_to_db(name, value):
        if name == 'effects':
            return [e.to_db() for e in value]
        return value

    async def buy(self, buyer: 'Player', quantity: int = 1):
        if self.price * quantity > buyer.balance.main_currency_balance:
            raise NotEnoughMoneyOnBalance
        item_id = str(self.id)
        current_quantity = buyer.backpack.get(item_id) or 0
        buyer.backpack[item_id] = current_quantity + quantity
        buyer.model.backpack[item_id] = current_quantity + quantity
        buyer.model.main_currency_balance -= self.price * quantity
        buyer.model.save()
