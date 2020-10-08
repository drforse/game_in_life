from aiogram.types import CallbackQuery

from aiogram_oop_framework.views import CallbackQueryView


class UseItem(CallbackQueryView):
    custom_filters = [lambda c: c.data.startswith('close_menu')]
    needs_reply_auth = False
    needs_satiety_level = 0

    @classmethod
    async def execute(cls, c: CallbackQuery):
        await c.message.delete()
