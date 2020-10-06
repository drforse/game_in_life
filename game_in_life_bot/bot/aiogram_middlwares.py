import logging

from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler
from aiogram.types import CallbackQuery


class AuthMiddlware(BaseMiddleware):
    def __init__(self, key_prefix='auth_'):
        self.prefix = key_prefix
        super(AuthMiddlware, self).__init__()

    async def on_process_callback_query(self, c: CallbackQuery, data: dict = None):
        menu_owner = c.data.split()[-1]
        if not menu_owner.isdigit():
            logging.debug('menu_owner not found while AuthMiddlware.on_process_callback_query processing')
            return

        menu_owner = int(menu_owner)
        if c.from_user.id != menu_owner:
            await c.answer('Это не твое меню', show_alert=True)
            raise CancelHandler
