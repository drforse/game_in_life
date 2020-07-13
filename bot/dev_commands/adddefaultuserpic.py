from aiogram.types import Message

from ..core import Command
from models import DefaultUserpicsModel


class AddDefaultUserPic(Command):

    @staticmethod
    async def execute(m: Message):
        if not m.reply_to_message:
            return
        if not m.reply_to_message.photo:
            return
        photo = m.reply_to_message.photo
        DefaultUserpicsModel.push_pic(photo_id=photo[0].file_id)
        await m.answer('Success')
