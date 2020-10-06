from aiogram.types import Message
from aiogram.dispatcher.handler import CancelHandler
from aiogram_oop_framework.views import CommandView, UserBaseView

from ....game.types import Player


class UserCommandView(CommandView, UserBaseView):
    needs_auth = True
    needs_reply_auth = True
    needs_satiety_level = 0

    @classmethod
    async def pre_execute(cls, m: Message):
        print(m)
        if cls.needs_reply_auth and not m.reply_to_message:
            try:
                await m.answer('Команда должна быть реплаем')
            except:
                pass
            raise CancelHandler
        users_to_auth = []
        if cls.needs_auth:
            users_to_auth.append(m.from_user)
        if cls.needs_reply_auth and m.reply_to_message:
            users_to_auth.append(m.reply_to_message.from_user)

        for user in users_to_auth:
            player = Player(tg_id=user.id)
            mention_url = f"https://t.me/{user.username}" if user.username else user.url
            mention = f'<a href="{mention_url}">{user.full_name}</a>'

            if not player.exists:
                try:
                    await m.answer('%s не играет.' % mention)
                except:
                    pass
                raise CancelHandler

            if m.chat.type in ['group', 'supergroup'] and m.chat.id not in player.chats:
                await player.join_chat(m.chat.id)

            if not player.alive:
                try:
                    await m.answer('%s мёртв.' % mention)
                except:
                    pass
                raise CancelHandler
            if player.satiety and player.satiety < cls.needs_satiety_level:
                await m.answer(
                    '%s слишком голоден! Нужный уровень сытости - %s, уровень сытости - %s.' % (
                        mention, cls.needs_satiety_level, round(player.satiety)))
                raise CancelHandler
