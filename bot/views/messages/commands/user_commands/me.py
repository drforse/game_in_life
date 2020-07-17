from aiogram.types import Message

from bot.views.base import UserCommandView
from game.types.player import Player, Eva, Adam
from senderman_roullette_api import exceptions as sexcs


class Me(UserCommandView):
    state = lambda: '*'
    needs_reply_auth = False
    needs_satiety_level = 0

    @classmethod
    async def execute(cls, m: Message, state=None):
        if m.chat.type == 'private':
            await cls.execute_in_private(m)
            return

        player = Player(tg_id=m.from_user.id)
        parent = Eva
        second_parent = Adam
        partner = None
        lover = None
        childs = []
        if player.parents[0] != '0':
            parent = Player(model_id=player.parents[0])
        if player.parents[1] != '0':
            second_parent = Player(model_id=player.parents[1])
        if player.partners.get(str(m.chat.id)):
            partner = Player(model_id=player.partners[str(m.chat.id)])
        if player.lovers.get(str(m.chat.id)):
            lover = Player(model_id=player.lovers[str(m.chat.id)])
        if player.childs.get(str(m.chat.id)):
            childs = [Player(model_id=child_id) for child_id in player.childs[str(m.chat.id)]]

        emojis = player.gender_emoji_reference
        text = 'Имя: %s %s\nВозраст: %s\nРодители: ' % (player.name, emojis[player.gender], player.age)

        parents = (parent, second_parent)
        for num, p in enumerate(parents):
            text += f'{p.name} {emojis[p.gender]}'
            if not p.alive:
                text += ' 🕯'
            if num != len(parents) - 1:
                text += ' | '
            else:
                text += '\n'

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
            text += '- %s %s' % (child.name,  emojis[child.gender])
            if not child.alive:
                text += ' 🕯'
            text += '\n'

        # pasyucoin_balance = player.balance.pasyucoin_currency_balance
        try:
            yulcoin_balance = await player.balance.yulcoin_currency_balance
        except (sexcs.UserNotFound, sexcs.SendermanRoulleteApiException):
            yulcoin_balance = None
        text += 'Баланс💰:\n'
        text += '   Кофеины (осн. вал.): ☕%s\n' % round(player.balance.main_currency_balance, 2)
        if yulcoin_balance is not None:
            text += '   Юлькоины: 🌯%s\n' % round(yulcoin_balance)

        text += 'Сытость: %s' % round(player.satiety)

        if player.photo_id:
            await m.answer_photo(player.photo_id, text)
        else:
            await m.answer(text)

    @classmethod
    async def execute_in_private(cls, m: Message, player: Player = None):
        player = player or Player(tg_id=m.from_user.id)

        if player.in_born_queue:
            await m.answer('Ждите своего рождения')
            return

        parent = Player(model_id=player.parents[0]) if player.parents[0] != '0' else Eva
        second_parent = Player(model_id=player.parents[1]) if player.parents[1] != '0' else Adam
        emojis = player.gender_emoji_reference
        text = 'Имя: %s %s\nВозраст: %s\nРодители: ' % (player.name, emojis[player.gender], player.age)
        parents = (parent, second_parent)
        for num, p in enumerate(parents):
            text += f'{p.name} {emojis[p.gender]}'
            if not p.alive:
                text += ' 🕯'
            if num != len(parents) - 1:
                text += ' | '
        text += '\n'

        # pasyucoin_balance = player.balance.pasyucoin_currency_balance
        try:
            yulcoin_balance = await player.balance.yulcoin_currency_balance
        except (sexcs.UserNotFound, sexcs.SendermanRoulleteApiException):
            yulcoin_balance = None
        text += 'Баланс💰:\n'
        text += '   Кофеины (осн. вал.): ☕%s\n' % round(player.balance.main_currency_balance, 2)
        if yulcoin_balance is not None:
            text += '   Юлькоины: 🌯%s\n' % round(yulcoin_balance)

        text += 'Сытость: %s' % round(player.satiety)

        if player.photo_id:
            await m.answer_photo(player.photo_id, text)
        else:
            await m.answer(text)
