from aiogram_oop_framework.views import MessageView
from aiogram.types import Message
from aiogram.dispatcher import FSMContext

from bot.aiogram_fsm import CreatePlayerForm
from bot.game import Game


class GetNewPlayerName(MessageView):
    state = lambda: CreatePlayerForm.set_pic
    content_types = ['text', 'photo', 'document']

    @classmethod
    async def execute(cls, m: Message, state: FSMContext = None, **kwargs):
        if not m.photo:
            await m.answer('Автарка должна быть картинкой')
            return
        photo_id = m.photo[-1].file_id
        async with state.proxy() as dt:
            name = dt['name']
            gender = dt['gender']
        await Game.create_new_player(m, m.from_user.id, name, gender, photo_id)
        await state.finish()
