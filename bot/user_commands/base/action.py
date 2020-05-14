from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import exceptions as aio_exceptions

from ...core import Command
from ...game import Game
from game.types import Player


class BaseAction(Command):

    # @classmethod
    # async def execute(cls, m: Message):
    #
    #     player = Player(tg_id=m.from_user.id)
    #     if m.from_user.id != m.reply_to_message.from_user.id:
    #         second_player = Player(tg_id=m.reply_to_message.from_user.id)
    #         return {'player': player, 'second_player': second_player}
    #     else:
    #         await cls.accept_action(data=f'{player.tg_id} {player.tg_id}', message=m)
    #         return
    #
    #     kb = InlineKeyboardMarkup()
    #     accept = InlineKeyboardButton('Секс',
    #                                   callback_data=f'action action accept {player.tg_id} {second_player.tg_id}')
    #     decline = InlineKeyboardButton('Нах',
    #                                    callback_data=f'action action decline {player.tg_id} {second_player.tg_id}')
    #     kb.add(accept, decline)
    #
    #     await m.answer('<a href="tg://user?id=%d">%s</a>, <a href="tg://user?id=%d">%s</a> предлагает поделать'
    #                    % (second_player.tg_id, second_player.name, player.tg_id, player.name), reply_markup=kb)

    @classmethod
    async def accept_action(cls, c: CallbackQuery = None, data: str = None, message: Message = None):
        if c:
            data = c.data

        data = data.split()
        user = int(data[-2])
        second_user = int(data[-1])
        action = data[1]
        player = Player(tg_id=user)
        second_player = Player(tg_id=second_user) if user != second_user else player

        msg = message or c.message
        try:
            await msg.delete()
        except aio_exceptions.MessageCantBeDeleted:
            pass
        await Game.process_accepted_action(action, cls.dp, cls.bot, msg.chat.id, player, second_player)

    @classmethod
    async def decline_action(cls, c: CallbackQuery):
        data = c.data.split()
        user = int(data[-2])
        second_user = int(data[-1])
        action = data[1]
        player = Player(tg_id=user)
        second_player = Player(tg_id=second_user)

        await Game.process_declined_action(action, c, player, second_player)
