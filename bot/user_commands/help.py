from aiogram.types import Message

from ..core import Command


class Help(Command):
    needs_auth = False
    needs_reply_auth = False

    @classmethod
    async def execute(cls, m: Message):
        await m.answer('https://telegra.ph/Game-In-Life---Igra-V-ZHizn-07-02')
