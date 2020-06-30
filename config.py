from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram import Bot
import os

API_TOKEN = os.environ['bot_token']
print(API_TOKEN)
DB_URL = os.environ['game_in_life_db_url']
print(DB_URL)

storage = MemoryStorage()
bot = Bot(API_TOKEN, parse_mode='html')
dp = Dispatcher(bot, storage=storage)


GAME_SPEED = 21600  # seconds == 1 age
DEVELOPERS = [879343317]
SEX_DELAY_INTERVAL = (10, 120)
