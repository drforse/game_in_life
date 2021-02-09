import logging

from aiogram.types import CallbackQuery
from aiogram_oop_framework.filters import filter_execute

from aiogram_oop_framework.views import CallbackQueryView

from ....game.cached_types import Theft
from ....game.types import Player
from ....game.types.job import Jobs
from ....game.types.perk import Perks


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
        #   [] make policeman's arrest perk level affect arresting
        player = Player(tg_id=q.from_user.id)
        if player.primary_job.id != Jobs.POLICEMAN:
            await q.answer("Но... ты не полицейский...")
            return

        dt = q.data.split()
        theft: Theft = Theft.get_last_with_players_in_chat(int(dt[2]), int(dt[3]), q.message.chat.id)

        catch = await theft.process_catch(player)
        await q.message.answer(
            f"Деньги ({theft.stolen_money}) и предметы возвращены законному владельцу.\n"
            f"Вор оштрафован на {catch.fine}.\n"
            f"Полицейский получил вознаграждение в размере {catch.catcher_reward}."
        )

        result = await player.up_perk(perk_id=Perks.ARREST)
        if not result == "new_perk_level":
            return
        perk = player.get_learned_perk_by_id(Perks.ARREST)
        await q.bot.send_message(
            player.tg_id,
            f"Congrats! Your perk {Perks.THEFT} is at new level - {perk.get_level()}!\n"
            f"Новые преимущества:\n"
            f"TODO")

        try:
            await q.message.delete()
        except:
            pass
