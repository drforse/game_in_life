from mongoengine import connect
import asyncio
from aiogram import executor
import multiprocessing

from config import dp, DB_URL
from bot.register_handlers import register_handlers
from bot.aiogram_middlwares import *
from users_queue import Queue


connect(host=DB_URL)
register_handlers()
dp.middleware.setup(CheckAgeMiddlware())
dp.middleware.setup(AuthMiddlware())

if __name__ == '__main__':
    multiprocessing.Process(target=Queue.run).start()
    executor.start_polling(dp, skip_updates=True)


# asyncio.gather(dp.skip_updates(), dp.start_polling(), Queue.run())
# asyncio.get_event_loop().run_forever()

# TODO:

# [] fuck processing
