from mongoengine import connect
from aiogram import executor
import multiprocessing
import logging

from .bot.manage import initialize_project
from .config import dp, DB_URL
from .users_queue import Queue


def run_users_queue():
    """
    Run .users_queue.Queue function with new database connection,
    only for new Process, in other case it should be just Queue.run()
    """
    connect(host=DB_URL)
    Queue.run()


def main():
    logging.basicConfig(level=logging.INFO)
    connect(host=DB_URL)
    multiprocessing.Process(target=run_users_queue).start()
    initialize_project(dp, dp.bot)
    executor.start_polling(dp, skip_updates=True)


# TODO:
# [] create auto-clearing db for not-used documents
