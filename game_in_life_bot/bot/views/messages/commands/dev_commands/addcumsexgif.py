from aiogram.types import Message

from ......bot.views.base import DevCommandView
from ......models import CumSexGifsModel


class AddCumSexGif(DevCommandView):

    @staticmethod
    async def execute(m: Message):
        if not m.reply_to_message:
            return
        if not m.reply_to_message.animation:
            return
        gif = m.reply_to_message.animation
        sex_types = m.text.split()[1:]
        for sex_type in sex_types:
            CumSexGifsModel.push_gif(sex_type, gif.file_id, gif.file_unique_id)
        await m.answer('Success')
