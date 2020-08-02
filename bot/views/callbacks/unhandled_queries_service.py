from aiogram.types import CallbackQuery

from aiogram_oop_framework.views import CallbackQueryView


class UnhandledQueriesService(CallbackQueryView):
    needs_reply_auth = False
    needs_satiety_level = 0
    index = 34

    @classmethod
    async def execute(cls, c: CallbackQuery):
        print(c)
        await c.answer()
