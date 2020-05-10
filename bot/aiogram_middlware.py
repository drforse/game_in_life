from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler
from aiogram.types import Message
from aiogram import Dispatcher

from models import *


class CheckAgeMiddlware(BaseMiddleware):
    def __init__(self, key_prefix='checkage_'):
        self.prefix = key_prefix
        super(CheckAgeMiddlware, self).__init__()

    async def on_process_message(self, m: Message, data: dict = None):
        user = User.get(tg_id=m.from_user.id, age__gte=0, age__lte=100)
        if not user:
            user = User.get(tg_id=m.from_user.id)
        if not user:
            return

        dp = Dispatcher.get_current()
        current_state = await (dp.current_state(chat=m.chat.id, user=m.from_user.id)).get_state()

        if user.age > 100:
            if (m.text != '/start' or m.chat.type != 'private') and not current_state:
                await m.reply('Вы умерли. Чтобы заного родиться, напишите /start мне в лс')
                raise CancelHandler
