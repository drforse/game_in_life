from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import re


from ......bot.views.base import UserCommandView
from .base.action import BaseAction


class Action(UserCommandView):

    @classmethod
    async def execute(cls, m: Message):
        if not re.match(BaseAction.custom_action_pattern, m.text):
            await m.answer('Команда не следует шаблону "/action действие | сообщение | ожидание | сообщение..."\n'
                           'Пример: /action сходить в кафе | {me} и {reply} пошли в кафе | 5 | {me} и {reply} пьют '
                           'кофе | 0 | {me} обняла {reply} и они разошлись по домам\n'
                           'Опционально: type:action_type сразу после команды'
                           'action_types: fuck')
            return

        await BaseAction.execute(m)
