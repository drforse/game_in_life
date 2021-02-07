import asyncio
from datetime import datetime

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from .....views.base import UserCommandView
from ......config import SECONDS_BEFORE_NEXT_CRIME
from ......game.types import Player, Item
from ......game.types.perk import Perks
from ......game.cached_types import Theft
from ......game.utils import get_level, get_time_to_catch_criminal
from ......redis_models import Theft as TheftModel


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

        last_theft: TheftModel = TheftModel.query.filter(
            criminal_id=m.from_user.id
        ).order_by("-created_at").first()
        if last_theft and not last_theft.is_completed:
            await m.answer("Вы еще не закончили Вашу предыдущую кражу!")
            return
        left_time = 0
        if last_theft:
            left_time = SECONDS_BEFORE_NEXT_CRIME - (datetime.now() - last_theft.created_at).total_seconds()
        if left_time > 0:
            await m.answer(f"Ты сейчас не можешь совершать преступления, подожди {int(left_time)} сек.")
            return

        user = m.from_user
        player = Player(tg_id=user.id)
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
                f"{player.name} попытался обокрасть {second_player.name}, но не смог", reply_markup=kb)
        else:
            stolen = await player.random_steal(second_player)
            text = f"{player.name} украл у {second_player.name} {stolen['money']} монет"
            for item_id, item_len in stolen["items"].items():
                item = Item(id=item_id)
                text += f", {item_len} {item.name}"

            Theft(chat_id=m.chat.id,
                  criminal_id=user.id,
                  victim_id=second_user.id,
                  stolen_money=stolen["money"],
                  stolen_items=stolen["items"]).save_to_db()

            msg = await m.answer(text, reply_markup=kb)

        await asyncio.sleep(10)  # get_time_to_catch_criminal(player.get_learned_perk_by_id(Perks.THEFT).xp))
        try:
            await msg.delete()
        except:
            pass

        theft: TheftModel = TheftModel.query.filter(
            criminal_id=user.id, victim_id=second_user.id, chat_id=m.chat.id
        ).order_by("-created_at").first()
        theft.is_completed = True
        theft.save()
        if theft.success:
            result = await player.up_perk(Perks.THEFT)
            await player.save_to_db()
            if result == "new_perk_level":
                perk = player.get_learned_perk_by_id(Perks.THEFT)
                await m.bot.send_message(
                    player.tg_id,
                    f"Congrats! Your perk {Perks.THEFT} is at new level - {get_level(perk.xp)}!\n"
                    f"Новые преимущества:\n"
                    f"Время на поимку после воровства теперь: {get_time_to_catch_criminal(perk.xp)} сек.")

