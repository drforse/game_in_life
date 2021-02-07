import logging

from aiogram.types import CallbackQuery
from aiogram_oop_framework.filters import filter_execute

from aiogram_oop_framework.views import CallbackQueryView

from ....game.types import Player
from ....game.types.job import Jobs
from ....redis_models import Theft as TheftModel


class CatchCriminal(CallbackQueryView):
    custom_filters = [lambda c: c.data.startswith('catch_criminal')]

    @classmethod
    async def execute(cls, q: CallbackQuery, state=None, **kwargs):
        logging.warning(
            f"CallPolice.execute method was called, but it isn't expected behavior, query:\n{q}")
        await q.answer()

    @classmethod
    @filter_execute(lambda c: c.data.startswith('catch_criminal theft'))
    async def catch_thief(cls, q: CallbackQuery):
        # TODO:
        #   [] make policeman's arrest perk level affect arresting and grow
        player = Player(tg_id=q.from_user.id)
        if player.primary_job.id != Jobs.POLICEMAN:
            await q.answer("Но... ты не полицейский...")
            return

        dt = q.data.split()
        theft: TheftModel = TheftModel.query.filter(
            criminal_id=int(dt[2]), victim_id=int(dt[3]), chat_id=q.message.chat.id
        ).order_by("-created_at").first()
        theft.success = False
        theft.is_completed = True
        theft.save()

        criminal = Player(tg_id=theft.criminal_id)
        victim = Player(tg_id=theft.victim_id)
        fine = theft.stolen_money * 0.5
        await criminal.balance.add_money_to_main_currency_balance(-(theft.stolen_money + fine))
        await victim.balance.add_money_to_main_currency_balance(theft.stolen_money)
        for item_id, quantity in theft.stolen_items.items():
            criminal.backpack[item_id] -= quantity
            victim.backpack[item_id] += quantity
        await criminal.save_to_db()
        await victim.save_to_db()

        await player.balance.add_money_to_main_currency_balance(fine)
        await q.message.answer(
            f"Деньги ({theft.stolen_money}) и предметы возвращены законному владельцу.\n"
            f"Вор оштрафован на {fine}.\n"
            f"Полицейский получил вознаграждение в размере {fine}."
        )
        try:
            await q.message.delete()
        except:
            pass
