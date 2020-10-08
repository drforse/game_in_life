from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import re


from ......bot.views.base import UserCommandView
from .base.action import BaseAction


class Action(UserCommandView, BaseAction):
    """
Использование: /action Описание | Текст 1 | время ожидания (число) | Текст 2
Пример: /action Пойти в кафе| я и кто-то пошли в кафе | 5 | мы потусили и разошлись по домам

Аргументы:
type:type*, который должен писаться сразу после команды (с пробелом xD)
*type может быть custom (default), fuck (станет то же самое, что и /fuck), marry, или date
Пример: /action type:fuck трахнуться | {me} сосет у {reply} | 1 | {reply} сосет у {me} | 1 | {reply} встает раком | 1 | {me} ебет {reply} в жопу | 1 | {reply} кончает кровью | 1 | {me} умирает от испуга | 1 | секс окончен

Дополнительно:
В текст можно добавить {me} (тегнет вас) и {reply} (тегнет человека, на сообщение которого было реплаем Ваше сообщения с командой /action)
Пример: /action Пойти в кафе|{me} и {reply} пошли в кафе | 5 | {me} и {reply} покушали и разошлись по домам
    """
    needs_satiety_level = 5
    command_description = "description | text | delay | text"

    @classmethod
    async def execute(cls, m: Message):
        if not re.match(BaseAction.custom_action_pattern, m.text):
            await m.answer('Команда не следует шаблону "/action действие | сообщение | ожидание | сообщение..."\n'
                           'Пример: /action сходить в кафе | {me} и {reply} пошли в кафе | 5 | {me} и {reply} пьют '
                           'кофе | 0 | {me} обняла {reply} и они разошлись по домам\n'
                           'Опционально: type:action_type сразу после команды'
                           'action_types: fuck')
            return

        await cls.execute_action(m)
