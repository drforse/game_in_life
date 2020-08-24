import typing

from ...models import UserModel, GroupModel


async def get_all_users() -> typing.Dict[int, UserModel]:
    unique_users = {}
    all_userdocs = UserModel.objects
    for userdoc in all_userdocs:
        if userdoc.tg_id not in unique_users:
            unique_users[userdoc.tg_id] = userdoc
    return unique_users


async def get_all_chats() -> typing.Dict[int, GroupModel]:
    return {group.chat_tg_id: group for group in GroupModel.objects}
