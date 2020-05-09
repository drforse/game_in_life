import asyncio
import time

from models import *
from bot.game import Game
from config import bot, game_speed


class Queue:
    is_running = False

    @classmethod
    async def run(cls):
        cls.is_running = True
        while cls.is_running:
            init = time.time()
            for user in User.objects(age__gte=0, age__lte=100):
                update = user.update_age()
                if update == 'died_now':
                    await Game.process_died_user(bot, user)
            end = time.time()
            await asyncio.sleep(game_speed - (end - init))

    @classmethod
    async def stop(cls):
        cls.is_running = False
