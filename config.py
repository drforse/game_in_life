from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram import Bot
import logging
import os


logging.basicConfig(level=logging.INFO)


API_TOKEN = os.environ['daddy_token']
DB_URL = os.environ['game_in_life_db_url']

storage = MemoryStorage()
bot = Bot(API_TOKEN, parse_mode='html')
dp = Dispatcher(bot, storage=storage)


game_speed = 50  # seconds == 1 age 21600
