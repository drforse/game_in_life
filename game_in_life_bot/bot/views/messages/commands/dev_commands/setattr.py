from aiogram.types import Message

from ......bot.views.base import DevCommandView
from ......models import UserModel


class SetAttr(DevCommandView):

    @staticmethod
    async def execute(m: Message):
        if not m.reply_to_message:
            return
        args = m.text.split(maxsplit=2)[1:]
        user_model = UserModel.get(tg_id=m.reply_to_message.from_user.id)
        if user_model:
            try:
                value = eval(args[1])
            except (NameError, SyntaxError):
                value = args[1]
            setattr(user_model, args[0], value)
            user_model.save()
            await m.answer("Success")
        else:
            await m.answer("User not found")
