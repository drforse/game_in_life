from aiogram.types import Message

from ......bot.views.base import DevCommandView
from ......models import SexGifsModel


class DelSexGif(DevCommandView):

    @staticmethod
    async def execute(m: Message):
        if not m.reply_to_message:
            return
        if not m.reply_to_message.animation:
            return
        gif = m.reply_to_message.animation
        sex_types = m.text.split()[1:]
        for sex_type in sex_types:
            SexGifsModel.pull_gif(sex_type, gif.file_unique_id)
        await m.answer('Success')
