import asyncio
import time
import logging

from mongoengine import connect

from .models import *
from .bot.game import Game
from .config import bot, GAME_SPEED


class Queue:
    is_running = False

    @classmethod
    def run(cls):
        cls.is_running = True
        while cls.is_running:
            init = time.time()
            users = UserModel.objects(age__gte=0, age__lte=100)
            logging.info(f'found {len(users)} users')
            for user in users:
                logging.info(f'pass user {user.tg_id}')
                update = user.update_age()
                logging.info(f'update == {update}')
                if update == 'died_now':
                    logging.info(f'pass user {user.tg_id} to process_died_user')
                    asyncio.get_event_loop().run_until_complete(Game.process_died_user(bot, user))
            end = time.time()
            try:
                time.sleep(GAME_SPEED - (end - init))
            except ValueError:
                pass

    @classmethod
    def stop(cls):
        cls.is_running = False