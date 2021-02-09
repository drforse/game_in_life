import random

from game_in_life_bot.config import MAX_LEVEL, MIN_SECONDS_TO_CATCH_CRIMINAL, SECONDS_TO_CATCH_CRIMINAL_MULTIPLIER


def pairwise(iterable):
    """s -> (s0, s1), (s2, s3), (s4, s5), ..."""
    a = iter(iterable)
    return zip(a, a)


def get_success(perk_level: int):
    return random.randint(perk_level, MAX_LEVEL) == perk_level


def get_time_to_catch_criminal(perk_level: int) -> int:
    return max([MIN_SECONDS_TO_CATCH_CRIMINAL,
                MAX_LEVEL / perk_level
                * SECONDS_TO_CATCH_CRIMINAL_MULTIPLIER])
