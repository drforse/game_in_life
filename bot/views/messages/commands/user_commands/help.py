from aiogram.types import Message

from bot.views.base import UserCommandView


class Help(UserCommandView):
    needs_auth = False
    needs_reply_auth = False
    needs_satiety_level = 0

    @classmethod
    async def execute(cls, m: Message):
        await m.answer('https://telegra.ph/Game-In-Life---Igra-V-ZHizn-07-02')