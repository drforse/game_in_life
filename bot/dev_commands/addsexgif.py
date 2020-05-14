from aiogram.types import Message

from ..core import Command
from models import SexGifs


class AddSexGif(Command):

    @staticmethod
    async def execute(m: Message):
        if not m.reply_to_message:
            return
        if not m.reply_to_message.animation:
            return
        gif = m.reply_to_message.animation
        sex_type = m.text.split(maxsplit=1)[1]
        SexGifs.push_gif(sex_type, gif.file_id)
        await m.answer('Success')
