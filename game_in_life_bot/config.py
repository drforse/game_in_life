from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram import Bot
import os
import asyncio

from bson import ObjectId

API_TOKEN = os.environ['game_in_life_bot_token']
DB_URL = os.environ['game_in_life_db_url']
REDIS_URL = os.environ['REDIS_URL']
SENDERMAN_SECURE_API_BOT_TOKEN = os.environ['senderman_secure_api_bot_token']

storage = MemoryStorage()
loop = asyncio.get_event_loop() or asyncio.new_event_loop()
bot = Bot(API_TOKEN, parse_mode='html', loop=loop)
dp = Dispatcher(bot, storage=storage, loop=loop)


GAME_SPEED = 21600  # seconds == 1 age
DEVELOPERS = [879343317]
SEX_DELAY_INTERVAL = (10, 120)
ACTIONS_FLOOD_REMOVE_DELAY = 120
PAGE_OFFSET = 5
UNEMPLOYED_JOB_ID = "unemployed"
XP_PER_LEVEL = 100
MAX_LEVEL = 100

# TODO: make it depend on level, last catch and last crime
SECONDS_BEFORE_NEXT_CRIME = 1

MIN_SECONDS_TO_CATCH_CRIMINAL = 10
SECONDS_TO_CATCH_CRIMINAL_MULTIPLIER = 3

# multiplies stolen money by MINIMUM_THEFT_CATCHER_REWARD_MULTIPLIER to get minimum reward,
# and if result > calculated reward, than uses it insteadof calculated reward
MINIMUM_THEFT_CATCHER_REWARD_MULTIPLIER = 0.5

# multiplies reward by THEFT_CATCHER_REWARD_MULTIPLIER to finish it's calculation
# (doesn't apply on reward gotten by stolen_money * MINIMUM_THEFT_CATCHER_REWARD_MULTIPLIER)
THEFT_CATCHER_REWARD_MULTIPLIER = 1.5

THEFT_FINE_MULTIPLIER = 0.5

CURRENCY_PRICES = {'pasyucoin': 0.5,
                   'main': 1.0,
                   'yulcoin': 0.5}

CHARACTERISTIC_VALUE_LIMITS = {'satiety': {'max': 100, 'min': 0}}
