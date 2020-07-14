from mongoengine import connect
from aiogram import executor
import multiprocessing
import logging

from bot.manage import initialize_project
from config import dp, DB_URL
from users_queue import Queue

logging.basicConfig(level=logging.INFO)

connect(host=DB_URL)

if __name__ == '__main__':
    multiprocessing.Process(target=Queue.run).start()
    initialize_project(dp, dp.bot)
    executor.start_polling(dp, skip_updates=True)


# TODO:
# [] create auto-clearing db for not-used documents
