from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler
from aiogram.types import Message

from models import *
from bot.game import Game


class CheckAgeMiddlware(BaseMiddleware):
    def __init__(self, key_prefix='checkage_'):
        self.prefix = key_prefix
        super(CheckAgeMiddlware, self).__init__()

    async def on_process_message(self, m: Message, data: dict):
        user = User.objects(tg_id=m.from_user.id)
        if not user:
            return

        user = user[0]
        update = user.update_age()
        if update == 'died_now':
            await Game.process_died_user(m, User)
        if user.age > 100:
            if m.text != '/start' or m.chat.type != 'private':
                await m.reply('Вы умерли. Чтобы заного родиться, напишите /start мне в лс')
                raise CancelHandler
