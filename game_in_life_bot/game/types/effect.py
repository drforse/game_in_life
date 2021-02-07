import asyncio

from ..exceptions import *
from ...config import CHARACTERISTIC_VALUE_LIMITS


class Effect:
    def __init__(self,
                 type_: str,
                 target_characteristic: str,
                 duration: int,
                 strength: float):
        self.type = type_
        self.target_characteristic = target_characteristic
        self.duration = duration
        self.strength = strength
        self.max_characteristic_value = CHARACTERISTIC_VALUE_LIMITS['satiety']['max']
        self.min_characteristic_value = CHARACTERISTIC_VALUE_LIMITS['satiety']['min']

    async def apply(self, target):
        async def update():
            setattr(target, self.target_characteristic, new_value)
            await target.save_to_db()
        for sec in range(self.duration):
            current_value = getattr(target.model, self.target_characteristic)
            change_value = self.strength / self.duration
            if self.type == 'increase':
                new_value = current_value + change_value
                if new_value > self.max_characteristic_value:
                    new_value = self.max_characteristic_value
                    await update()
                    break
            elif self.type == 'decrease':
                new_value = current_value - change_value
                if new_value < self.max_characteristic_value:
                    new_value = self.max_characteristic_value
                    await update()
                    break
            else:
                raise EffectTypeNotKnown(self.type)
            await update()
            await asyncio.sleep(1)

    def to_db(self):
        return {'type_': self.type,
                'target_characteristic': self.target_characteristic,
                'duration': self.duration,
                'strength': self.strength}
