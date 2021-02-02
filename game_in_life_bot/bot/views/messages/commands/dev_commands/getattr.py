from aiogram.types import Message

from ......bot.views.base import DevCommandView
from ......models import UserModel


class GetAttr(DevCommandView):

    @staticmethod
    async def execute(m: Message):
        if not m.reply_to_message:
            return
        args = m.text.split()[1:]
        user_model = UserModel.get(tg_id=m.reply_to_message.from_user.id)
        if user_model:
            await m.answer(str(getattr(user_model, args[0])))
        else:
            await m.answer("User not found")
