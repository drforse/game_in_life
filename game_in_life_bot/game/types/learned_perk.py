import math

from bson import ObjectId

from .perk import Perk
from ...config import XP_PER_LEVEL


class LearnedPerk:
    def __init__(self, perk: ObjectId, xp: int):
        self.perk = Perk(id=perk)
        self.xp = xp

    def get_level(self):
        return math.floor(self.xp / XP_PER_LEVEL)

    def to_db(self):
        return {"perk": self.perk.id,
                "xp": self.xp}
