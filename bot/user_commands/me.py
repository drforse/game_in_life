from aiogram.types import Message

from ..core import Command
from game.types import Player


class Me(Command):
    needs_reply_auth = False

    @classmethod
    async def execute(cls, m: Message):
        if m.chat.type == 'private':
            await cls.execute_in_private(m)
            return

        player = Player(tg_id=m.from_user.id)
        parent = 'Ева'
        second_parent = 'Адам'
        partner = None
        lover = None
        childs = []
        if player.parents[0] != '0':
            parent = Player(model_id=player.parents[0]).name
        if player.parents[1] != '0':
            second_parent = Player(model_id=player.parents[1]).name
        if player.partners.get(str(m.chat.id)):
            partner = Player(model_id=player.partners[str(m.chat.id)])
        if player.lovers.get(str(m.chat.id)):
            lover = Player(model_id=player.lovers[str(m.chat.id)])
        if player.childs.get(str(m.chat.id)):
            childs = [Player(model_id=child_id) for child_id in player.childs[str(m.chat.id)]]
        text = ('Имя: %s\nПол: %s\nВозраст: %s\nРодители: %s, %s\n' %
                (player.name, player.gender, player.age, parent, second_parent))
        if partner:
            if partner.gender == 'female':
                s = 'Жена: %s'
            elif partner.gender == 'male':
                s = 'Муж: %s'
            else:
                s = 'Партнер: %s'
            text += s % partner.name

        if lover:
            if lover.gender == 'female':
                s = 'Девушка: %s'
            elif lover.gender == 'male':
                s = 'Парень: %s'
            else:
                s = 'Встречается с: %s'
            text += s % lover.name

        if childs:
            text += '\nДети:\n'
        for child in childs:
            if not child.exists:
                continue
            text += '- %s' % child.name
            if not child.alive:
                text += '🕯'
            text += '\n'

        await m.answer(text)

    @classmethod
    async def execute_in_private(cls, m: Message, player: Player = None):
        player = player or Player(tg_id=m.from_user.id)

        if player.in_born_queue:
            await m.answer('Ждите своего рождения')
            return

        parent = Player(model_id=player.parents[0]).name if player.parents[0] != '0' else 'Ева'
        second_parent = Player(model_id=player.parents[1]).name if player.parents[1] != '0' else 'Адам'
        await m.answer('Имя: %s\nПол: %s\nВозраст: %s\nРодители: %s, %s\n' %
                       (player.name, player.gender, player.age, parent, second_parent))
