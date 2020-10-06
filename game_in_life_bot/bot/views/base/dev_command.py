from aiogram.types import Message
from aiogram_oop_framework.views import CommandView, UserBaseView
from aiogram_oop_framework.filters.filters import filter_execute

from ....config import DEVELOPERS


class DevCommandView(CommandView, UserBaseView):
    """
    needed for auth purposes
    """

    @classmethod
    @filter_execute(lambda m: m.from_user.id not in DEVELOPERS)
    async def execute_for_non_devs(cls, m: Message, state=None, **kwargs):
        return
