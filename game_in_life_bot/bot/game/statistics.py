import typing

from aiogram import Bot
from aiogram.utils import exceptions

from ...models import UserModel, GroupModel


async def get_all_users(exclude_chats: typing.List[int] = None) -> typing.Dict[int, UserModel]:
    unique_users = {}
    exclude_chats = exclude_chats or []
    all_userdocs = UserModel.objects
    for userdoc in all_userdocs:
        if userdoc.tg_id in unique_users:
            continue
        userchats = userdoc.chats.copy()
        for chat in exclude_chats:
            if chat in userchats:
                userchats.remove(chat)
        if not userchats and userchats != userdoc.chats:
            continue
        unique_users[userdoc.tg_id] = userdoc
    return unique_users


async def get_all_chats(separate_kicked=False, bot: Bot = None) -> typing.Dict:
    if not separate_kicked:
        return {group.chat_tg_id: group for group in GroupModel.objects}
    result = {'kicked': {}}
    for group in GroupModel.objects:
        try:
            await bot.send_chat_action(group.chat_tg_id, 'typing')
            result[group.chat_tg_id] = group
        except (exceptions.BotKicked, exceptions.ChatNotFound):
            result['kicked'][group.chat_tg_id] = group
    return result
