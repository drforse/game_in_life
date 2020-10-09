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
            loop = asyncio.get_event_loop()
            users = UserModel.objects(age__gte=0, age__lte=100)
            logging.info(f'found {len(users)} users')
            for user in users:
                logging.info(f'pass user {user.tg_id}')
                update = user.update_age()
                logging.info(f'update == {update}')
                if update == 'died_now':
                    logging.info(f'pass user {user.tg_id} to process_died_user')
                    loop.run_until_complete(Game.process_died_user(bot, user))

            logging.info("process awaiting born users")
            awaiting_born_users = UserModel.objects(age=-1)
            logging.info(f"awaiting born users: {[u.tg_id for u in awaiting_born_users]}")
            for user in awaiting_born_users:
                logging.info(f"process awaiting born user: {user.tg_id}")
                possible_parents = loop.run_until_complete(
                    Game.get_users_availiable_for_children(user, bot))
                logging.info(f"possible parents for user {user.tg_id}: {[u.tg_id for u in possible_parents]}")
                if len(possible_parents) < 2:
                    user.parents = ['0', '0']
                    user.age = 0
                    user.save()
                    logging.info(f"{user.tg_id} has been born from Adam and Eva")
                    text = "Вы родились от Адама и Евы!"
                    try:
                        loop.run_until_complete(
                            bot.send_message(user.tg_id, text))
                        logging.info(f"{user.tg_id} has been notified about his born")
                    except Exception as e:
                        logging.info(f"{user.tg_id} has not been notified about his born because {e}")
                        pass
            end = time.time()
            try:
                time.sleep(GAME_SPEED - (end - init))
            except ValueError:
                pass

    @classmethod
    def stop(cls):
        cls.is_running = False
