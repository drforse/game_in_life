from aiogram.types import Message

from ......bot.aiogram_fsm import CreateCountryForm
from ......bot.views.base import UserCommandView
from ......bot.game import Game
from ......game.types.player import Player, Country
from .me import Me


class Start(UserCommandView):
    needs_auth = False
    needs_reply_auth = False
    ignore_busy = True

    @classmethod
    async def execute(cls, m: Message):
        if m.chat.type == 'private':
            await cls.execute_in_private(m)
            return
        country = Country(chat_tg_id=m.chat.id)
        if not country.exists:
            await m.answer('Привет. Придумайте название своей стране и напишите реплаем на это сообщение '
                           '(пока не придумаете, я тут писать не буду)')
            await CreateCountryForm.set_name.set()
            return

        player = Player(tg_id=m.from_user.id)
        if not player.exists:
            await m.answer('Привет, незнакомец. Ты в стране %s. Напиши мне в лс, чтобы играть.' % country.name)
            return
        if not player.alive:
            await m.answer('Привет, мертвец. Ты в стране %s. Напиши мне в лс, чтобы ожить. '
                           'Мертвые не играют' % country.name)
            return
        await m.answer('Привет, %s. Ты находишься в стране %s' % (player.name, country.name))

    @classmethod
    async def execute_in_private(cls, m: Message):
        player = Player(tg_id=m.from_user.id)

        if not player.exists:
            await Game.process_new_user(m)
            return
        if not player.alive and not player.in_born_queue:
            await Game.process_rebornig_user(m)
            return

        await Me.execute_in_private(m, player)
