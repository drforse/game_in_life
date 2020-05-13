from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler
from aiogram.types import Message, CallbackQuery
from aiogram import Dispatcher
import logging

from models import *
from bot import user_commands
from game.types import Player


class CheckAgeMiddlware(BaseMiddleware):
    def __init__(self, key_prefix='checkage_'):
        self.prefix = key_prefix
        super(CheckAgeMiddlware, self).__init__()

    async def on_process_message(self, m: Message, data: dict = None):
        command = data.get('command')
        command = command.command if command else command
        if command == 'date':
            await m.answer('Not implemented yet')
            return
        user = User.get(tg_id=m.from_user.id)
        if not user:
            return

        dp = Dispatcher.get_current()
        current_state = await (dp.current_state(chat=m.chat.id, user=m.from_user.id)).get_state()

        if user.age > 100:
            if (command != 'start' or m.chat.type != 'private') and not current_state:
                await m.reply('Вы умерли. Чтобы заново родиться, напишите /start мне в лс')
                raise CancelHandler


class AuthMiddlware(BaseMiddleware):
    def __init__(self, key_prefix='auth_'):
        self.prefix = key_prefix
        super(AuthMiddlware, self).__init__()

    async def on_process_message(self, m: Message, data: dict = None):
        users_to_auth = []
        command = data.get('command')
        command_found = False
        if command:
            command = command.command
        else:
            return

        for user_command in [value for key, value in user_commands.__dict__.items() if type(value) == type]:
            if not command == user_command.__name__.lower():
                continue
            if user_command.needs_auth:
                users_to_auth.append(m.from_user.id)
            if user_command.needs_reply_auth and m.reply_to_message:
                users_to_auth.append(m.reply_to_message.from_user.id)
            if user_command.needs_reply_auth and not m.reply_to_message:
                await m.answer('Команда должна быть реплаем')
                raise CancelHandler
            command_found = True
            break

        if not command_found:
            return

        for user in users_to_auth:
            player = Player(tg_id=user)
            member = await m.bot.get_chat_member(m.chat.id, user)
            if not player.exists:
                await m.answer('<a href="tg://user?id=%s">%s</a> не играет.' %
                               (player.tg_id, member.user.first_name or member.user.last_name))
                raise CancelHandler
            if not player.alive:
                await m.answer('<a href="tg://user?id=%s">%s</a> мёртв.' %
                               (player.tg_id, member.user.first_name or member.user.last_name))
                raise CancelHandler

    async def on_process_callback_query(self, c: CallbackQuery, data: dict = None):
        menu_owner = c.data.split()[-1]
        if not menu_owner.isdigit():
            logging.debug('menu_owner not found while AuthMiddlware.on_process_callback_query processing')
            return

        menu_owner = int(menu_owner)
        if c.from_user.id != menu_owner:
            await c.answer('Это не твое меню', show_alert=True)
            raise CancelHandler
