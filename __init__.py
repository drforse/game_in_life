from mongoengine import connect
from aiogram import executor
import multiprocessing
import logging

from config import dp, DB_URL
from bot.register_handlers import register_handlers
from bot.aiogram_middlwares import AuthMiddlware
from users_queue import Queue

logging.basicConfig(level=logging.INFO)

connect(host=DB_URL)
register_handlers()
dp.middleware.setup(AuthMiddlware())

if __name__ == '__main__':
    multiprocessing.Process(target=Queue.run).start()
    executor.start_polling(dp, skip_updates=True)


# TODO:
# [] create auto-clearing db for not-used documents
# [x] clear users in DB
# [x] test getting the last (by date) document of user by tg_id, if not working: make work
