from aiogram.types import Message

from ......bot.views.base import UserCommandView
from ......bot.game import Game
from ......game.types.player import Player


class Suicide(UserCommandView):
    """Бля, ну че непонятного-то? Выйти в окно! Теперь дошло? Нет? Броситься под поезд, перерезать вены, повеситься, наорать на мамку, понял? Если до сих пор не понял, то даже хз, как тебе помочь, может тебе пойти в школу для "особо-одаренных"?"""
    needs_auth = False
    needs_reply_auth = False
    needs_satiety_level = 1
    command_description = "suicide"

    @staticmethod
    async def execute(m: Message):
        player = Player(tg_id=m.from_user.id)
        if not player.alive:
            await m.answer('А ты и так не жив')
            return

        if not player.exists:
            await m.answer('А ты и не рождался никогда даже. '
                           'Напиши мне /start в личку, чтобы начать играть :3')
            return

        await Game.process_died_user(m.bot, player)
        await m.answer('Прощай... 🕯')
