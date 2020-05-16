from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import re

from .base.action import BaseAction


class Action(BaseAction):

    @classmethod
    async def execute(cls, m: Message):
        if not re.match(cls.custom_action_pattern, m.text):
            await m.answer('Команда не следует шаблону "/action действие | сообщение | ожидание | сообщение..."\n'
                           'Пример: /action сходить в кафе | {me} и {reply} пошли в кафе | 5 | {me} и {reply} пьют '
                           'кофе | 0 | {me} обняла {reply} и они разошлись по домам\n'
                           'Опционально: type:action_type сразу после команды'
                           'action_types: fuck')
            return

        await cls.base_execute(m)
