import math
import random

from game_in_life_bot.config import XP_PER_LEVEL, MAX_LEVEL, MIN_SECONDS_TO_CATCH_CRIMINAL, \
    SECONDS_TO_CATCH_CRIMINAL_MULTIPLIER


def pairwise(iterable):
    """s -> (s0, s1), (s2, s3), (s4, s5), ..."""
    a = iter(iterable)
    return zip(a, a)


def get_success(perk_xp: int):
    level = get_level(perk_xp)
    return random.randint(level, MAX_LEVEL) == level


def get_level(xp: int):
    return math.floor(xp / XP_PER_LEVEL)


def get_time_to_catch_criminal(perk_xp: int) -> int:
    return max([MIN_SECONDS_TO_CATCH_CRIMINAL,
                MAX_LEVEL / get_level(perk_xp)
                * SECONDS_TO_CATCH_CRIMINAL_MULTIPLIER])
