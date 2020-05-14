from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import exceptions as aio_exceptions

from ..core import Command
from ..game import Game
from game.types import Player


class Fuck(Command):

    @classmethod
    async def execute(cls, m: Message):

        player = Player(tg_id=m.from_user.id)
        if m.from_user.id != m.reply_to_message.from_user.id:
            second_player = Player(tg_id=m.reply_to_message.from_user.id)
        else:
            await cls.accept_fuck(data=f'{player.tg_id} {player.tg_id}', message=m)
            return

        kb = InlineKeyboardMarkup()
        accept = InlineKeyboardButton('Секс', callback_data=f'fuck accept {player.tg_id} {second_player.tg_id}')
        decline = InlineKeyboardButton('Нах', callback_data=f'fuck decline {player.tg_id} {second_player.tg_id}')
        kb.add(accept, decline)

        await m.answer('<a href="tg://user?id=%d">%s</a>, <a href="tg://user?id=%d">%s</a> предлагает поебаться'
                       % (second_player.tg_id, second_player.name, player.tg_id, player.name), reply_markup=kb)

    @classmethod
    async def accept_fuck(cls, c: CallbackQuery = None, data: str = None, message: Message = None):
        if c:
            data = c.data

        user = int(data.split()[-2])
        second_user = int(data.split()[-1])
        player = Player(tg_id=user)
        second_player = Player(tg_id=second_user) if user != second_user else player

        msg = message or c.message
        try:
            await msg.delete()
        except aio_exceptions.MessageCantBeDeleted:
            pass
        await Game.process_fuck(cls.dp, cls.bot, msg.chat.id, player, second_player)

    @staticmethod
    async def decline_fuck(c: CallbackQuery):
        user = int(c.data.split()[-2])
        second_user = int(c.data.split()[-1])
        player = Player(tg_id=user)
        second_player = Player(tg_id=second_user)

        await c.answer('Блин, а я уже камеру приготовил (9((')
        await c.message.edit_text(
            '<a href="tg://user?id=%d">%s</a> не хочет ебаться с <a href="tg://user?id=%d">%s</a>' %
            (second_player.tg_id, second_player.name, player.tg_id, player.name),
            reply_markup=None)
