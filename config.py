from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram import Bot
import os

API_TOKEN = os.environ['bot_token']
DB_URL = os.environ['game_in_life_db_url']

storage = MemoryStorage()
bot = Bot(API_TOKEN, parse_mode='html')
dp = Dispatcher(bot, storage=storage)


GAME_SPEED = 21600  # seconds == 1 age
DEVELOPERS = [879343317]
