from aiogram.types import Message
from aiogram_oop_framework.utils import get_help
from aiogram_oop_framework.filters import filter_execute

from ......bot.views.base import UserCommandView


class Help(UserCommandView):
    """Посмотреть мануал по игре.
Или можешь написать /help command, чтобы посмотреть справку по конкретной команде (пример: /help help). Ах да, ты же этим и занят!"""
    needs_auth = False
    needs_reply_auth = False
    ignore_busy = True
    command_description = "get help; /help &lt;command&gt;"

    @classmethod
    async def execute(cls, m: Message):
        await m.answer(
            'https://telegra.ph/Game-In-Life---Igra-V-ZHizn-07-02\n'
            'Напиши /help command, чтобы посмотреть справку по конкретной команде (пример: /help help).')

    @classmethod
    @filter_execute(lambda m: m.get_args())
    async def execute_with_args(cls, m: Message):
        help_ = get_help(m.get_args())
        if help_:
            await m.answer(help_)
        else:
            await m.answer(f"Извините, но хелп для команды {m.get_args()} не найден")
