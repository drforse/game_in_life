from aiogram.types import Message

from game_in_life_bot.bot.views.base import UserCommandView
from game_in_life_bot.game.types import Player
from .base.action import BaseAction


class Fuck(UserCommandView, BaseAction):
    """Эта команда - для любителей потрахаться в игре (ой, да кого я обманываю? Все игра для этого).
Напиши ее реплаем на сообщение предмета свеого желания (также возможны кастомные тексты, как в /action (/help action))"""
    needs_satiety_level = 20
    dead_allowed = True
    command_description = "fuck people, fuck yourself, fuck everybody"

    @classmethod
    async def execute(cls, m: Message, state=None, **kwargs):
        user = m.from_user
        player = Player(tg_id=user.id)
        if not player.alive:
            await m.answer('%s мёртв.' % user.get_mention(player.name))
            return

        args = m.get_args()
        m.text = '/action' + ' type:fuck '
        m.text += args or 'поебаться |'
        await cls.execute_action(m)
