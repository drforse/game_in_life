from aiogram.types import Message
from aiogram_oop_framework.utils import Commands

from ......bot.views.base import UserCommandView


class CommandsView(UserCommandView):
    """Посмотреть список команд и их краткое описание"""
    needs_auth = False
    needs_reply_auth = False
    ignore_busy = True
    command_description = "see all commands"
    commands = ['commands']
    append_commands = False
    set_my_commands = 'first'

    @classmethod
    async def execute(cls, m: Message):
        commands = Commands().find_all_commands(filter_=lambda v: v.get_help())
        await m.answer(commands.format(separator=" - "))
