from aiogram.types import Message

from ......bot.views.base import UserCommandView
from ......game.types import Player
from ......models import UserModel


class Players(UserCommandView):
    state = lambda: '*'
    needs_auth = False
    needs_reply_auth = False
    ignore_busy = True

    @classmethod
    async def execute(cls, m: Message, state=None):
        players = UserModel.objects(chats=m.chat.id)
        s = ""
        dead_players = {}
        included_players = {}
        for pl in players:
            player = Player(model=pl)
            if player.in_born_queue:
                included_players[player.tg_id] = player
            elif not player.alive:
                dead_players[player.tg_id] = player
            elif player.alive:
                included_players[player.tg_id] = player

        for pl in dead_players:
            if pl not in included_players:
                included_players[pl] = dead_players[pl]

        for _, player in included_players.items():
            mention = player.name
            try:
                member = await m.bot.get_chat_member(m.chat.id, player.tg_id)
                if member.user.username:
                    mention = f'<a href="https://t.me/{member.user.username}">{player.name}</a>'
            except:
                continue

            s += f"{mention}"
            if player.in_born_queue:
                s += " 🤰"
            elif not player.alive:
                s += " 🕯"
            s += "\n"

        await m.answer(s)
