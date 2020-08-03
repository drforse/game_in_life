from aiogram_oop_framework.views.content_types_views import NewChatMembersView
from aiogram.types import Message
from aiogram.dispatcher import FSMContext

from game.types import Player


class ProcessNewChatMembers(NewChatMembersView):

    @classmethod
    async def execute(cls, m: Message, state: FSMContext = None, **kwargs):
        for member in m.new_chat_members:
            player = Player(tg_id=member.id)
            if player.exists and m.chat.id not in player.chats:
                await player.join_chat(m.chat.id)
