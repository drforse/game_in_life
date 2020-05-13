from __future__ import annotations

import logging
import random
import typing
import asyncio
from pymongo.collection import ObjectId

from models import *


class Player:

    cant_marry_reason_exaplanation = {'married': 'Вы уже в браке в этой стране',
                                      'partner_married': 'Вы не можете вступить в брак с тем, кто уже в браке',
                                      'partner_dead': 'Вы не можете вступить в брак с тем, кто не жив',
                                      'too_young': 'Вступать в брак можно только с 16-ти лет, до 16-ти можно только встречаться - /date',
                                      'cant_marry_self': 'Нельзя вступать в брак с самим собой'}

    def __init__(self, tg_id: int = None, model_id: ObjectId = None, model: User = None):
        self.tg_id = tg_id
        self.exists = False
        self.id = model_id
        self.name = None
        self.gender = None
        self.age = None
        self.chats = None
        self.parents = None
        self.partners = None
        self.childs = None
        self.alive = None
        self.in_born_queue = None
        self.model = model
        self.update_from_db(model)

    async def create(self, name, gender, age, chats=(), parents=()) -> Player:
        model = User(tg_id=self.tg_id, name=name, gender=gender, age=age, chats=list(chats), parents=list(parents))
        model.save()
        self.update_from_db(model)
        return self

    def update_from_db(self, model: User = None):
        model = model if model else User.get(pk=self.id) if self.id else\
            User.get(tg_id=self.tg_id)
        self.model = model
        if not model:
            self.exists = False
            return
        self.tg_id = model.tg_id
        self.id = model.id
        self.name = model.name
        self.gender = model.gender
        self.age = model.age
        self.chats = model.chats
        self.parents = model.parents
        self.partners = model.partners
        self.childs = model.childs
        self.alive = -1 < model.age < 101
        self.in_born_queue = model.age == -1
        self.exists = True

    async def join_chat(self, chat_tg_id):
        self.model.update(push__chats=chat_tg_id)

    async def die(self, update_from_db=False):
        if update_from_db:
            self.update_from_db()
        if self.model.age < 101:
            self.model.update_age(101)

        output = {}

        childs_list = []
        logging.info(f'process died user {self.tg_id}')

        for chat in self.partners:
            childs = self.childs.get(chat, [])
            childs_list += childs
            partner_player = Player(model_id=self.partners[chat])
            await partner_player.divorce(chat, partner_player)
            if not partner_player.alive:
                continue
            country = Country(chat_tg_id=int(chat))
            logging.info(f'process died user {self.tg_id}: notify partner {partner_player.tg_id}')
            output[partner_player.tg_id] = 'Ваш партнер в стране %s, %s - умер...' % (country.name, self.name)

        for child in childs_list:
            child_user = Player(model_id=child)
            if not child_user.alive:
                continue
            logging.info(f'process died user {self.tg_id}: notify child {child_user.tg_id}')
            output[child_user.tg_id] = 'Ваш родитель, %s - умер...' % self.name

        for parent in self.parents:
            if parent == "0":
                continue
            parent_player = Player(model_id=parent)
            if not parent_player.alive:
                continue
            logging.info(f'process died user {self.tg_id}: notify parent {parent_player.tg_id}')
            output[parent_player.tg_id] = 'Ваше чадо, %s - умерло...' % self.name

        logging.info(f'process died user {self.tg_id}: finished')

        return output

    async def marry(self, chat_tg_id: int, partner_tg_id: int):
        partner = Player(tg_id=partner_tg_id)

        can_marry = await self.can_marry(chat_tg_id, partner)
        if not can_marry['result']:
            return self.cant_marry_reason_exaplanation[can_marry['reason']]

        self.model.update(__raw__={'$set': {f'partners.{chat_tg_id}': partner.id}})
        partner.model.update(__raw__={'$set': {f'partners.{chat_tg_id}': self.id}})
        return ('Поздавляем <a href="tg://user?id=%d">%s</a> и <a href="tg://user?id=%d">%s</a> со свадьбой' %
                (self.tg_id, self.name, partner.tg_id, partner.name))

    async def can_marry(self, chat_tg_id: int, partner: Player) -> typing.Dict:
        """

        :param chat_tg_id:
        :param partner:
        :return: {'result': boolean, 'reason': str}
        """
        if not partner.alive:
            return {'result': False, 'reason': 'partner_dead'}
        if self.tg_id == partner.tg_id:
            return {'result': False, 'reason': 'cant_marry_self'}
        if self.age < 16 or partner.age < 16:
            return {'result': False, 'reason': 'too_young'}
        if str(chat_tg_id) in self.partners:
            return {'result': False, 'reason': 'married'}
        if str(chat_tg_id) in partner.partners:
            return {'result': False, 'reason': 'partner_married'}

        return {'result': True, 'reason': ''}

    async def divorce(self, chat_tg_id: int, partner: typing.Union[User, Player, int, ObjectId] = None):
        if partner:
            partner_model = await self.resolve_user(partner, 'User')
        else:
            partner_model = User(model_id=self.model.partners[str(chat_tg_id)])
        self.model.unset_partner(chat_tg_id)
        partner_model.unset_partner(chat_tg_id)

    async def fuck(self, chat_id, partner: typing.Union[User, Player, int, ObjectId], delay: int = 300):
        partner = await self.resolve_user(partner, 'Player')
        if self.tg_id == partner.tg_id:
            verb_form = 'кончил' if self.gender == 'male' else 'кончила' if self.gender == 'female' else 'кончил(а)'
            start_message = '<a href="tg://user?id=%d">%s</a> дрочит.' % (self.tg_id, self.name)
            end_message = '<a href="tg://user?id=%d">%s</a> %s.' % (self.tg_id, self.name, verb_form)
        else:
            start_message = '<a href="tg://user?id=%d">%s</a> и <a href="tg://user?id=%d">%s</a> пошли трахаться :3' %\
                            (self.tg_id, self.name, partner.tg_id, partner.name)
            end_message = '<a href="tg://user?id=%d">%s</a> и <a href="tg://user?id=%d">%s</a> закончили трахаться' % \
                          (self.tg_id, self.name, partner.tg_id, partner.name)

        yield start_message
        await asyncio.sleep(delay)

        child = None
        female = self if self.gender == 'female' else partner if partner.gender == 'female' else None
        male = self if self.gender == 'male' else partner if partner.gender == 'male' else None
        if male and female and female.age >= 12:

            country = Country(chat_id)
            childs_queue = await country.get_childs_queue()
            if childs_queue:
                child = random.choice(childs_queue)

        if child:
            mother = female
            father = male
            end_message += ('\n\n<a href="tg://user?id=%d">%s</a> забеременела и родила '
                            '<a href="tg://user?id=%d">%s</a>' % (mother.tg_id, mother.name, child.tg_id,
                                                                  child.name)
                            )
            child = Player(model=child)
            await Player.born(child, mother, father, chat_id)

        yield end_message

    async def born(self, mother: Player, father: Player, chat: typing.Union[Country, int]):
        if isinstance(chat, Country):
            chat = Group.chat_tg_id
        self.model.delete()
        child = Player(tg_id=self.tg_id)
        child = await child.create(name=self.name, gender=self.gender, age=0,
                                   chats=self.chats, parents=[mother.id, father.id])
        mother.model.push_child(chat, child.id)
        father.model.push_child(chat, child.id)

    @staticmethod
    async def resolve_user(user: typing.Union[User, Player, int, ObjectId], result_type: str = 'Player'):
        user_type = type(user)
        if user_type == Player:
            if result_type == 'Player':
                return user
            model = user.model
        elif user_type == User:
            model = user
        elif user_type == ObjectId:
            model = User.get(id=user, age__gte=0, age__lte=100)
        elif user_type == int:
            model = User.get(tg_id=user, age__gte=0, age__lte=100)
        else:
            raise TypeError('partner arg type must be User, Player, int or ObjectId')

        if result_type == 'Player':
            return Player(model=model)
        elif result_type == 'User':
            return model


class Country:
    def __init__(self, chat_tg_id):
        self.chat_tg_id = chat_tg_id
        self.id = None
        self.name = None
        self.exists = False
        self.update_from_db()

    def update_from_db(self, model: Group = None):
        model = model or Group.get(chat_tg_id=self.chat_tg_id)
        if not model:
            self.exists = False
            return
        self.id = model.id
        self.name = model.name
        self.exists = True

    async def create(self, name: str) -> Country:
        model = Group(chat_tg_id=self.chat_tg_id, name=name)
        model.save()
        self.update_from_db(model)
        self.exists = True
        return self

    async def get_childs_queue(self) -> typing.Optional[typing.Iterable[User]]:
        return User.objects(age=-1, chats=self.chat_tg_id)
