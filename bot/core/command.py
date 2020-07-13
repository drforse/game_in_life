from aiogram.types import Message

from config import *


class Command:
    dp = dp
    bot = bot
    needs_auth = True
    needs_reply_auth = True
    needs_satiety_level = 30

    @staticmethod
    async def execute(m: Message):
        pass

    @classmethod
    def register(cls, callback=None, *custom_filters, commands=None, regexp=None,
                 content_types=None, state=None, run_task=None, set_commands=True, **kwargs):
        callback = callback or cls.execute
        if set_commands and not commands:
            commands = [cls.__name__.lower()]
        cls.dp.register_message_handler(callback=callback, *custom_filters, commands=commands, regexp=regexp,
                                        content_types=content_types, state=state, run_task=run_task, **kwargs)

    @classmethod
    def register_inline(cls, callback=None, *custom_filters, state=None, run_task=None, **kwargs):
        callback = callback or cls.execute
        cls.dp.register_inline_handler(callback, *custom_filters,
                                       state=state, run_task=run_task, **kwargs)

    @classmethod
    def reg_callback(cls, callback=None, *custom_filters, state=None, run_task=None, **kwargs):
        callback = callback or cls.execute
        cls.dp.register_callback_query_handler(callback, *custom_filters, state=state, run_task=run_task, **kwargs)
