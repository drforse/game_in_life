import asyncio

from ..exceptions import *


class Effect:
    def __init__(self, type_: str, target_characteristic: str, duration: int, strength: float):
        self.type = type_
        self.target_characteristic = target_characteristic
        self.duration = duration
        self.strength = strength

    async def apply(self, target):
        for sec in range(self.duration):
            current_value = getattr(target.model, self.target_characteristic)
            change_value = self.strength / self.duration
            if self.type == 'increase':
                new_value = current_value + change_value
            elif self.type == 'decrease':
                new_value = current_value - change_value
            else:
                raise EffectTypeNotKnown(self.type)
            setattr(target, self.target_characteristic, new_value)
            setattr(target.model, self.target_characteristic, new_value)
            target.model.save()
            await asyncio.sleep(1)

    def to_db(self):
        return {'type_': self.type,
                'target_characteristic': self.target_characteristic,
                'duration': self.duration,
                'strength': self.strength}
