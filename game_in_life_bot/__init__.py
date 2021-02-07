import asyncio

from mongoengine import connect
from aiogram import executor
import multiprocessing
import logging

from .bot.manage import initialize_project
from .config import dp, DB_URL
from .users_queue import Queue
from .game.actions.storage import ActionsStorage


def run_users_queue():
    """
    Run .users_queue.Queue function with new database connection,
    only for new Process, in other case it should be just Queue.run()
    """
    connect(host=DB_URL)
    Queue.run()


def on_shutdown():
    logging.info("Running on_shutdown...")
    from .redis_models import Theft

    for theft in Theft.query.execute():
        theft.delete()


def main():
    logging.basicConfig(level=logging.INFO)
    connect(host=DB_URL)
    multiprocessing.Process(target=run_users_queue).start()
    loop = asyncio.get_event_loop() or asyncio.new_event_loop()
    initialize_project(dp, dp.bot, loop=loop)
    dp.actions_storage = ActionsStorage()
    executor.start_polling(dp, skip_updates=True, on_shutdown=on_shutdown)


# TODO:
# [] create auto-clearing db for not-used documents
