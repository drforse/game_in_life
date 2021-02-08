import asyncio

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from .....views.base import UserCommandView
from ......game.types import Player, Item, CrimesStatuses
from ......game.types.perk import Perks
from ......game.cached_types import Theft
from ......game.utils import get_level, get_time_to_catch_criminal


class Steal(UserCommandView):
    """Попробовать украсть что-то у человека"""
    needs_satiety_level = 5
    command_description = "try to steal something"

    @classmethod
    async def execute(cls, m: Message, state=None, **kwargs):
        await m.answer("Not ready yet!")
        return

        if m.reply_to_message.from_user.id == m.from_user.id:
            await m.answer("You can't steal from youself!")
            return

        user = m.from_user
        player = Player(tg_id=user.id)
        crimes_status = await player.get_crimes_status()
        if crimes_status.status == CrimesStatuses.IN_PROCESS:
            await m.answer("Вы еще не закончили Вашу предыдущую кражу!")
        if crimes_status == CrimesStatuses.HIDING:
            await m.answer(f"Ты сейчас не можешь совершать преступления, "
                           f"подожди {int(crimes_status.left_time)} сек.")
        if crimes_status in CrimesStatuses.BUSY:
            return

        if Perks.THEFT not in player.learned_perks_ids:
            await m.answer("У вас нет способности красть!")
            return

        second_user = m.reply_to_message.from_user
        second_player = Player(tg_id=second_user.id)
        success = True  # get_success(player.get_learned_perk_by_id(Perks.THEFT).xp)

        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("Позвать полицию", callback_data="call_police theft"))
        kb.add(InlineKeyboardButton(
            "Поймать вора",

            # . is at the end of callback_data because else auth will be required (see aiogram_middlewares.py)
            callback_data=f"catch_criminal theft {user.id} {second_user.id} ."
        ))

        if not success:
            msg = await m.answer(
                f"{player.name} попытался обокрасть {second_player.name}, но не смог",
                reply_markup=kb)
        else:
            theft = await player.random_steal(second_player, m.chat.id)
            text = f"{player.name} украл у {second_player.name} {theft.stolen_money} монет"
            for item_id, item_len in theft.stolen_items.items():
                item = Item(id=item_id)
                text += f", {item_len} {item.name}"
            msg = await m.answer(text, reply_markup=kb)

        await asyncio.sleep(10)  # get_time_to_catch_criminal(player.get_learned_perk_by_id(Perks.THEFT).xp))
        try:
            await msg.delete()
        except:
            pass

        theft = Theft.get_last_with_players_in_chat(player.tg_id, second_player.tg_id, m.chat.id)
        theft.complete()

        if not theft.success:
            return
        result = await player.up_perk(Perks.THEFT)

        if not result == "new_perk_level":
            return
        perk = player.get_learned_perk_by_id(Perks.THEFT)
        await m.bot.send_message(
            player.tg_id,
            f"Congrats! Your perk {Perks.THEFT} is at new level - {get_level(perk.xp)}!\n"
            f"Новые преимущества:\n"
            f"Время на поимку после воровства теперь: {get_time_to_catch_criminal(perk.xp)} сек.")

