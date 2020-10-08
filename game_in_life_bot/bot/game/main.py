import asyncio
import traceback

from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import Bot, Dispatcher
import logging
import typing
import random

from ...models import *
from ...game.types.player import Player
from ...config import ACTIONS_FLOOD_REMOVE_DELAY
from ..aiogram_fsm import CreatePlayerForm, ActionForm


class Game:

    @staticmethod
    async def process_new_user(m: Message):
        await m.answer('Привет. Мы с тобой незнакомы. Как тебя зовут?')
        await CreatePlayerForm.set_name.set()

    @staticmethod
    async def process_rebornig_user(m: Message):
        await m.answer('Привет. Ну что, по новой? Как тебя зовут?')
        await CreatePlayerForm.set_name.set()

    @classmethod
    async def create_new_player(cls, m: Message, user_id: int, name: str, gender: str, photo_id: str = None):

        old_user = UserModel.get(tg_id=user_id)
        chats = old_user.chats if old_user else []

        user = UserModel(tg_id=user_id, name=name, age=-1, gender=gender, photo_id=photo_id, chats=chats)
        user.save()
        text = 'Создан игрок с данными:\nИмя: %s\nПол: %s\nВозраст: 0\n' % (user.name, user.gender)
        if not await cls.get_users_availiable_for_children(user, m.bot):
            text += 'Родители: Ева, Адам\n'
            user.parents = ['0', '0']
            user.age = 0
            user.save()
        else:
            user.save()
            text += ('\nЖдите своего рождения. Чтобы родиться, Вы должны написать /start хотя бы в одной из групп с '
                     'ботом (чем больше групп, тем выше скорость рождения).')
        await m.answer_photo(user.photo_id, text, reply_markup=ReplyKeyboardRemove())

    @staticmethod
    async def get_users_availiable_for_children(user: UserModel, bot: Bot):
        chats = user.chats
        result = []
        for chat in chats:
            females_in_marriage = []
            males_in_marriage = []
            users_in_marriage = UserModel.objects(__raw__={f'partners.{chat}': {'$exists': True},
                                                           'age': {'$lte': 0, '$gte': 100}})
            for u in users_in_marriage:
                if u.gender == 'female':
                    females_in_marriage.append(u)
                elif u.gender == 'male':
                    males_in_marriage.append(u)
            females = []
            males = []
            for user in UserModel.objects(chats=chat, age__gte=12, age__lte=100):
                try:
                    member = await bot.get_chat_member(chat, user.tg_id)
                except:
                    user.update(pull__chats=chat)
                    continue
                if member.status in ['left', 'kicked']:
                    user.update(pull__chats=chat)
                    continue

                if user.gender == 'female' and user not in females_in_marriage:
                    females.append(user)
                elif user.gender == 'male' and user not in males_in_marriage:
                    males.append(user)

            result += users_in_marriage  # + users_dating

            if len(females) > len(males):
                females = females[:len(males)]
            else:
                males = males[:len(females)]

            result += females + males
        return result

    @staticmethod
    async def process_died_user(bot: Bot, player: typing.Union[int, UserModel, Player]):
        if isinstance(player, int):
            player = Player(tg_id=player)
        elif isinstance(player, UserModel):
            player = Player(model=player)
        output = await player.die()
        for msg in output:
            try:
                await bot.send_message(msg, output[msg])
            except:
                pass

    @classmethod
    async def process_accepted_action(cls, action: 'Action', dp: Dispatcher,
                                      chat_tg_id: int, user: Player, second_user: Player):
        for u in {user.tg_id, second_user.tg_id}:
            current_state = dp.current_state(chat=u, user=u)
            await current_state.set_state(ActionForm.busy)

        results = []
        try:
            results = await action.do(bot=dp.bot)
        except:
            logging.error(traceback.format_exc())
            await dp.bot.send_message(chat_tg_id, "Sorry, some error occured")
        finally:
            for u in {user.tg_id, second_user.tg_id}:
                await dp.current_state(chat=u, user=u).finish()

            await asyncio.sleep(ACTIONS_FLOOD_REMOVE_DELAY)
            removed_ids = []
            for result in results:
                if not hasattr(result, "sent_message"):
                    continue
                try:
                    if result.sent_message.message_id not in removed_ids:
                        await result.sent_message.delete()
                        removed_ids.append(result.sent_message.message_id)
                except:
                    continue

    @classmethod
    async def process_declined_action(cls, action: str, callback_query,
                                      player: Player, second_player: Player, custom_data=None):
        callback_answer = ''
        edit_text = ''
        verb_form = ('отказал' if second_player.gender == 'male' else 'отказала'
                               if second_player.gender == 'female' else 'отказал(а)')
        if action == 'fuck':
            callback_answer = 'Блин, а я уже камеру приготовил (9(('
            edit_text = '<a href="tg://user?id=%d">%s</a> не хочет ебаться с <a href="tg://user?id=%d">%s</a>'
        elif action == 'marriage':
            callback_answer = 'А жаль...'
            edit_text = ('<a href="tg://user?id=%d">%s</a> {} в браке '
                         '<a href="tg://user?id=%d">%s</a>'.format(verb_form))
        elif action == 'dating':
            callback_answer = 'А жаль...'
            edit_text = ('<a href="tg://user?id=%d">%s</a> {} в романтических '
                         'отношениях <a href="tg://user?id=%d">%s</a>'.format(verb_form))
        elif action == 'custom' and custom_data:
            edit_text = ('<a href="tg://user?id=%d">%s</a> не хочет {} с '
                         '<a href="tg://user?id=%d">%s</a>'.format(custom_data['action']))
        elif action == 'custom':
            edit_text = 'Кастомные сообщения не были даны или предложение устарело'
            await callback_query.message.edit_text(edit_text, reply_markup=None)
            return

        edit_text = edit_text % (second_player.tg_id, second_player.name, player.tg_id, player.name)
        await callback_query.answer(callback_answer)
        await callback_query.message.edit_text(edit_text, reply_markup=None)
