from aiogram.types import Message

from .base.action import BaseAction


class Fuck(BaseAction):

    @classmethod
    async def execute(cls, m: Message):

        args = m.get_args()
        m.text = '/action' + ' type:fuck '
        m.text += args or 'поебаться |'
        print(m.text)
        await cls.base_execute(m)
