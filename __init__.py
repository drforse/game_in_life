from mongoengine import connect
from aiogram import executor

from config import dp, DB_URL
from bot.register_handlers import register_handlers
from bot.aiogram_middlware import CheckAgeMiddlware


connect(host=DB_URL)
register_handlers()
dp.middleware.setup(CheckAgeMiddlware())
executor.start_polling(dp, skip_updates=True)
