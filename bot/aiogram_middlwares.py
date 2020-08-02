from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler
from aiogram.types import Message, CallbackQuery
import logging

from .views.base import UserCommandView, DevCommandView
from game.types.player import Player
from config import *


class AuthMiddlware(BaseMiddleware):
    def __init__(self, key_prefix='auth_'):
        self.prefix = key_prefix
        super(AuthMiddlware, self).__init__()

    async def on_process_message(self, m: Message, data: dict = None):
        users_to_auth = []
        command = data.get('command')
        if command:
            command_text = command.command
        else:
            return

        main_player = Player(tg_id=m.from_user.id)

        user_commands_dict = {view.__name__.lower(): view for view in UserCommandView.__subclasses__()}
        dev_commands_dict = {view.__name__.lower(): view for view in DevCommandView.__subclasses__()}
        user_command = user_commands_dict.get(command_text)
        dev_command = dev_commands_dict.get(command_text)
        if not user_command and not dev_command:
            return
        elif dev_command:
            if m.from_user.id not in DEVELOPERS:
                raise CancelHandler
        elif user_command:
            if user_command.needs_auth:
                users_to_auth.append(m.from_user.id)
            if user_command.needs_reply_auth and m.reply_to_message:
                users_to_auth.append(m.reply_to_message.from_user.id)
            if user_command.needs_reply_auth and not m.reply_to_message:
                try:
                    await m.answer('Команда должна быть реплаем')
                except:
                    pass
                raise CancelHandler

        for user in users_to_auth:
            player = Player(tg_id=user) if user != main_player.tg_id else main_player
            member = await m.bot.get_chat_member(m.chat.id, user)
            if m.chat.type in ['group', 'supergroup'] and m.chat.id not in player.chats:
                await player.join_chat(m.chat.id)

            if not player.exists:
                try:
                    await m.answer('<a href="tg://user?id=%s">%s</a> не играет.' %
                                   (player.tg_id, member.user.first_name or member.user.last_name))
                except:
                    pass
                raise CancelHandler
            if not player.alive:
                try:
                    await m.answer('<a href="tg://user?id=%s">%s</a> мёртв.' %
                                   (player.tg_id, member.user.first_name or member.user.last_name))
                except:
                    pass
                raise CancelHandler
            if player.satiety and player.satiety < user_command.needs_satiety_level:
                await m.answer(f'{player.name} слишком голоден! Нужный уровень сытости - {user_command.needs_satiety_level}, '
                               f'ваш уровень сытости - {round(main_player.satiety)}.')
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
