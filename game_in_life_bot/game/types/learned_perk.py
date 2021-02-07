from bson import ObjectId

from .perk import Perk


class LearnedPerk:
    def __init__(self, perk: ObjectId, xp: int):
        self.perk = Perk(id=perk)
        self.xp = xp

    def to_db(self):
        return {"perk": self.perk.id,
                "xp": self.xp}
