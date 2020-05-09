from mongoengine import connect
import asyncio

from config import dp, DB_URL
from bot.register_handlers import register_handlers
from bot.aiogram_middlware import CheckAgeMiddlware
from users_queue import Queue


connect(host=DB_URL)
register_handlers()
dp.middleware.setup(CheckAgeMiddlware())

asyncio.gather(dp.skip_updates(), dp.start_polling(), Queue.run())
asyncio.get_event_loop().run_forever()
