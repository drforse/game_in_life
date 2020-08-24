from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram import Bot
import os

API_TOKEN = os.environ['game_in_life_bot_token']
DB_URL = os.environ['game_in_life_db_url']
SENDERMAN_SECURE_API_BOT_TOKEN = os.environ['senderman_secure_api_bot_token']

storage = MemoryStorage()
bot = Bot(API_TOKEN, parse_mode='html')
dp = Dispatcher(bot, storage=storage)


GAME_SPEED = 21600  # seconds == 1 age
DEVELOPERS = [879343317]
SEX_DELAY_INTERVAL = (10, 120)

CURRENCY_PRICES = {'pasyucoin': 0.5,
                   'main': 1.0,
                   'yulcoin': 0.5}

CHARACTERISTIC_VALUE_LIMITS = {'satiety': {'max': 100, 'min': 0}}
