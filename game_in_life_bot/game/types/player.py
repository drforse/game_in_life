from __future__ import annotations

import logging
import random
import typing
import asyncio

from bson.objectid import ObjectId
from mongoengine.queryset.visitor import Q

from ..actions.actions_factory import ActionsFactory
from ...models import *
from .balance import Balance
from .item import Item
from ..exceptions import *


class Player:

    cant_marry_reason_exaplanation = {'married': 'Вы уже в браке в этой стране',
                                      'partner_married': 'Вы не можете вступить в брак с тем, кто уже в браке',
                                      'partner_dead': 'Вы не можете вступить в брак с тем, кто не жив',
                                      'too_young': 'Вступать в брак можно только с 16-ти лет, '
                                                   'до 16-ти можно только встречаться - /date',
                                      'cant_marry_self': 'Нельзя вступать в брак с самим собой',
                                      'is_dating_another_person': 'Вы не можете вступить в брак с кем-то, '
                                                                  'если Вы встречаетесь с другим человеклм',
                                      'partner_is_dating_another_person': 'Этот человек состоит в романтических '
                                                                          'отношениях с кем-то другим'}

    cant_date_reason_exaplanation = {'lover_dead': 'Вы не можете встречаться с тем, кто не жив',
                                     'cant_date_self': 'Вы не можете встречаться с самим собой',
                                     'is_dating': 'Вы уже состоите в романтичекских отношениях',
                                     'married': 'Вы в браке',
                                     'lover_married': 'Вы не можете встречаться с тем, кто состоит в браке',
                                     'lover_dating': 'Этот человек с кем-то уже встречается'}

    gender_emoji_reference = {'male': '♂️', 'female': '♀️', 'transgender': '♂️♀️'}

    def __init__(self, model_id: ObjectId = None, tg_id: int = None, model: UserModel = None):
        self.id = model_id
        self.tg_id = tg_id
        self.exists = False
        self.name = None
        self.gender = None
        self.photo_id = None
        self.age = None
        self.chats = None
        self.parents = None
        self.partners = None
        self.lovers = None
        self.childs = None
        self.balance = Balance()
        self.satiety = None
        self.backpack = None
        self.model: UserModel = model
        self.update_from_db(model)

    async def create(self, name, gender, age, chats=(), parents=()) -> Player:
        model = UserModel(tg_id=self.tg_id, name=name, gender=gender, age=age,
                          chats=list(chats), parents=list(parents), photo_id=self.photo_id)
        model.save()
        self.update_from_db(model)
        return self

    def update_from_db(self, model: UserModel = None):
        if not model:
            model = UserModel.get(id=self.id) if self.id else UserModel.get(tg_id=self.tg_id)
        self.model = model
        if not model:
            self.exists = False
            return
        self.id = model.id
        self.tg_id = model.tg_id
        self.name = model.name
        self.gender = model.gender
        self.photo_id = model.photo_id
        self.age = model.age
        self.chats = model.chats
        self.parents = model.parents
        self.partners = model.partners
        self.lovers = model.lovers
        self.childs = model.childs
        self.balance = Balance(self)
        self.satiety = model.satiety
        self.backpack = model.backpack
        self.exists = True

    @property
    def alive(self):
        if self.age is not None:
            return -1 < self.age < 101

    @property
    def in_born_queue(self):
        return self.age == -1

    async def join_chat(self, chat_tg_id):
        self.model.update(push__chats=chat_tg_id)

    async def leave_chat(self, chat_tg_id):
        self.model.update(pull__chats=chat_tg_id)

    async def action(self, action: str, chat_id: int, partner: typing.Union[UserModel, Player, int],
                     delay: int = 300, custom_data: str = None) -> 'Action':
        partner = await self.resolve_user(partner, 'Player')
        Action_ = ActionsFactory.get(action)
        action_ = Action_(5, self, partner, chat_id)
        await action_.complete(delay, custom_data)
        return action_

    async def born(self, mother: Player, father: Player, chat: typing.Union[Country, int]):
        if isinstance(chat, Country):
            chat = GroupModel.chat_tg_id
        self.model.delete()
        child = self
        child = await child.create(name=self.name, gender=self.gender, age=0,
                                   chats=self.chats, parents=[mother.id, father.id])
        mother.model.push_child(chat, child.id)
        father.model.push_child(chat, child.id)

    async def die(self, update_from_db=False):
        if update_from_db:
            self.update_from_db()
        if self.model.age < 101:
            self.model.update_age(101)
            self.age = 101

        logging.info(f'process died user {self.id} ({self.tg_id})')

        output = await self.notify_partners_about_death()
        output.update(await self.notify_lovers_about_death())
        output.update((await self.notify_childs_about_death()))
        output.update((await self.notify_parents_about_death()))

        logging.info(f'process died user {self.id} ({self.tg_id}): finished')

        return output

    async def notify_partners_about_death(self) -> dict:
        output = {}
        for chat in self.partners:
            partner_player = Player(model_id=self.partners[chat])
            await self.divorce(chat, partner_player)
            if not partner_player.alive:
                continue
            country = Country(chat_tg_id=int(chat))
            logging.info(f'process died user {self.id} ({self.tg_id}):'
                         f' notify partner {partner_player.id} ({partner_player.tg_id})')
            output[partner_player.tg_id] = 'Ваш партнер в стране %s, %s - умер...' % (country.name, self.name)
        return output

    async def notify_lovers_about_death(self) -> dict:
        output = {}
        for chat in self.lovers:
            lover_player = Player(model_id=self.lovers[chat])
            await self.break_up(chat, lover_player)
            if not lover_player.alive:
                continue
            country = Country(chat_tg_id=int(chat))
            logging.info(f'process died user {self.id} ({self.tg_id}):'
                         f' notify lover {lover_player.id} ({lover_player.tg_id})')
            output[lover_player.tg_id] = 'Ваша вторая половинка в стране %s, %s - умер...' % (country.name, self.name)
        return output

    async def notify_childs_about_death(self) -> dict:
        output = {}
        childs = []
        for chat in self.childs:
            childs = self.childs.get(chat, [])
            childs += childs
        for child_id in childs:
            child_user = Player(model_id=child_id)
            if not child_user.alive:
                continue
            logging.info(f'process died user {self.id} ({self.tg_id}):'
                         f' notify child {child_user.id} ({child_user.tg_id})')
            output[child_id] = 'Ваш родитель, %s - умер...' % self.name
        return output

    async def notify_parents_about_death(self) -> dict:
        output = {}
        for parent_id in self.parents:
            if parent_id == "0":
                continue
            parent_player = Player(model_id=parent_id)
            if not parent_player.alive:
                continue
            logging.info(f'process died user {self.id} ({self.tg_id}):'
                         f' notify parent {parent_player.id} ({parent_player.tg_id})')
            output[parent_player.tg_id] = 'Ваше чадо, %s - умерло...' % self.name
        return output

    async def can_marry(self, chat_tg_id: int, partner: Player) -> typing.Dict:
        """

        :param chat_tg_id:
        :param partner:
        :return: {'result': boolean, 'reason': str}
        """
        if not partner.alive:
            return {'result': False, 'reason': 'partner_dead'}
        if self.id == partner.id:
            return {'result': False, 'reason': 'cant_marry_self'}
        if self.age < 16 or partner.age < 16:
            return {'result': False, 'reason': 'too_young'}
        if self.lovers.get(str(chat_tg_id), partner.id) != partner.id:
            return {'result': False, 'reason': 'is_dating_another_person'}
        if partner.lovers.get(str(chat_tg_id), self.id) != self.id:
            return {'result': False, 'reason': 'partner_is_dating_another_person'}
        if str(chat_tg_id) in self.partners:
            return {'result': False, 'reason': 'married'}
        if str(chat_tg_id) in partner.partners:
            return {'result': False, 'reason': 'partner_married'}

        return {'result': True, 'reason': ''}

    async def can_date(self, chat_tg_id: int, lover: Player) -> typing.Dict:
        """

        :param chat_tg_id:
        :param lover:
        :return: {'result': boolean, 'reason': str}
        """
        if not lover.alive:
            return {'result': False, 'reason': 'lover_dead'}
        if self.id == lover.id:
            return {'result': False, 'reason': 'cant_date_self'}
        if str(chat_tg_id) in self.lovers:
            return {'result': False, 'reason': 'is_dating'}
        if str(chat_tg_id) in self.partners:
            return {'result': False, 'reason': 'married'}
        if str(chat_tg_id) in lover.partners:
            return {'result': False, 'reason': 'lover_married'}
        if str(chat_tg_id) in lover.lovers:
            return {'result': False, 'reason': 'lover_dating'}

        return {'result': True, 'reason': ''}

    async def divorce(self, chat_tg_id: int, partner: typing.Union[UserModel, Player, int] = None):
        if partner:
            partner_model = await self.resolve_user(partner, 'User')
        else:
            partner_model = UserModel(id=self.model.partners[str(chat_tg_id)])
        self.model.unset_partner(chat_tg_id)
        partner_model.unset_partner(chat_tg_id)

    async def break_up(self, chat_tg_id: int, lover: typing.Union[UserModel, Player, int] = None):
        if lover:
            lover_model = await self.resolve_user(lover, 'User')
        else:
            lover_model = UserModel(id=self.model.lovers[str(chat_tg_id)])
        self.model.unset_lover(chat_tg_id)
        lover_model.unset_lover(chat_tg_id)

    async def get_childs_and_parents(self, chat_id: int,
                                     partner: Player) -> typing.Dict[str, typing.Union[UserModel, Player, list]]:
        children = []
        female = self if self.gender == 'female' else partner if partner.gender == 'female' else None
        male = self if self.gender == 'male' else partner if partner.gender == 'male' else None
        if male and female and female.age >= 12 and male.alive and female.alive:
            country = Country(chat_id)
            childs_queue = await country.get_childs_queue()
            if childs_queue:
                child = random.choice(childs_queue)
                children.append(child)
                childs_queue.remove(child)
            if childs_queue:
                child_1 = random.choice(childs_queue)
                children.append(child_1)
                childs_queue.remove(child_1)
            if childs_queue:
                child_2 = random.choice(childs_queue)
                children.append(child_2)
                childs_queue.remove(child_2)

        return {'children': children, 'mother': female, 'father': male}

    async def get_sex_types(self, partner: Player) -> dict:
        if self.id == partner.id:
            if self.gender == 'male':
                sex_type = 'masturbate_male'
            elif self.gender == 'female':
                sex_type = 'masturbate_female'
            else:
                sex_type = 'masturbate_transgender'
        elif self.gender == 'male' and partner.gender == 'female':
            sex_type = 'hetero'
        elif self.gender == 'female' and partner.gender == 'male':
            sex_type = 'hetero'
        elif self.gender == 'female' and partner.gender == 'female':
            sex_type = 'lesbian'
        elif self.gender == 'male' and partner.gender == 'male':
            sex_type = 'gay'
        elif ((self.gender == 'female' and partner.gender == 'transgender') or
              (self.gender == 'transgender' and partner.gender == 'female')):
            sex_type = 'transgender_and_female'
        elif ((self.gender == 'male' and partner.gender == 'transgender') or
              (self.gender == 'transgender' and partner.gender == 'male')):
            sex_type = 'transgender_and_male'
        else:
            sex_type = 'transgenders'

        universal_sex_type = 'universal' if not sex_type.startswith('masturbate') else 'masturbate_universal'

        if not partner.alive:
            sex_type = "dead_" + sex_type
            universal_sex_type = "dead_" + universal_sex_type

        return {'main': sex_type, 'universal': universal_sex_type}

    @staticmethod
    async def get_possible_sex_gifs(sex_type: str, universal_sex_type: str) -> list:
        possible_gif_models = SexGifsModel.objects(Q(type=sex_type) | Q(type=universal_sex_type))
        possible_gifs = []
        for model in possible_gif_models:
            possible_gifs += [gifdict['file_id'] for gifdict in model.gif_ids]
        return possible_gifs

    @staticmethod
    async def get_possible_cum_sex_gifs(sex_type: str, universal_sex_type: str) -> list:
        possible_gif_models = CumSexGifsModel.objects(Q(type=sex_type) | Q(type=universal_sex_type))
        possible_gifs = []
        for model in possible_gif_models:
            possible_gifs += [gifdict['file_id'] for gifdict in model.gif_ids]
        return possible_gifs

    @staticmethod
    async def resolve_user(user: typing.Union[UserModel, Player, int], result_type: str = 'Player'):
        user_type = type(user)
        if user_type == Player:
            if result_type == 'Player':
                return user
            model = user.model
        elif user_type == UserModel:
            model = user
        elif user_type == int:
            model = UserModel.get(tg_id=user, age__gte=0, age__lte=100)
        else:
            raise TypeError('partner arg type must be User, Player or int')

        if result_type == 'Player':
            return Player(model=model)
        elif result_type == 'User':
            return model

    async def use(self, item: Item, target, quantity: int = 1):
        item_id = str(item.id)
        if item_id not in self.backpack:
            raise NoItemInBuildpack
        if self.backpack[item_id] < quantity:
            raise NotEnoughItems
        for i in range(quantity):
            self.backpack[item_id] -= 1
            self.model.save()
            loop = asyncio.get_event_loop()
            for e in item.effects:
                loop.create_task(e.apply(target))


class Country:
    def __init__(self, chat_tg_id):
        self.chat_tg_id = chat_tg_id
        self.id = None
        self.name = None
        self.exists = False
        self.update_from_db()

    def update_from_db(self, model: GroupModel = None):
        model = model or GroupModel.get(chat_tg_id=self.chat_tg_id)
        if not model:
            self.exists = False
            return
        self.id = model.id
        self.name = model.name
        self.exists = True

    async def create(self, name: str) -> Country:
        model = GroupModel(chat_tg_id=self.chat_tg_id, name=name)
        model.save()
        self.update_from_db(model)
        self.exists = True
        return self

    async def get_childs_queue(self) -> typing.Optional[typing.List[UserModel]]:
        return list(UserModel.objects(age=-1, chats=self.chat_tg_id))


class Eva:
    gender = 'female'
    name = 'Ева'
    alive = True


class Adam:
    gender = 'male'
    name = 'Адам'
    alive = True
