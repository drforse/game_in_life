import asyncio
import time
import logging

from models import *
from bot.game import Game
from config import bot, game_speed


class Queue:
    is_running = False

    @classmethod
    def run(cls):
        cls.is_running = True
        while cls.is_running:
            init = time.time()
            users = User.objects(age__gte=0, age__lte=100)
            logging.info(f'found {len(users)} users')
            for user in users:
                logging.info(f'pass user {user.tg_id}')
                update = user.update_age()
                logging.info(f'update == {update}')
                if update == 'died_now':
                    logging.info(f'pass user {user.tg_id} to process_died_user')
                    print(user, user.partners)
                    asyncio.get_event_loop().run_until_complete(Game.process_died_user(bot, user))
            end = time.time()
            try:
                time.sleep(game_speed - (end - init))
            except ValueError:
                pass

    @classmethod
    def stop(cls):
        cls.is_running = False
