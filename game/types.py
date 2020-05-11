from __future__ import annotations

import logging

import typing
from pymongo.collection import ObjectId

from models import *


class Player:
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
        self.model = model
        if not model:
            self.update_from_db(model)

    async def create(self, name, gender, age, chats=(), parents=()) -> Player:
        model = User(tg_id=self.tg_id, name=name, gender=gender, age=age, chats=list(chats), parents=list(parents))
        model.save()
        self.update_from_db(model)
        self.exists = True
        return self

    def update_from_db(self, model: User = None):
        model = model if model else User.get(pk=self.id) if self.id else\
            User.get(tg_id=self.tg_id, age__gte=0, age__lte=100)
        self.model = model
        if not model:
            self.exists = False
            return
        self.id = model.id
        self.name = model.name
        self.gender = model.gender
        self.age = model.age
        self.chats = model.chats
        self.parents = model.parents
        self.partners = model.partners
        self.childs = model.childs
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
            partner_user = User.get(pk=self.partners[chat], age__gte=0, age__lte=100)
            if not partner_user:
                continue
            partner_user.unset_partner(chat)
            country = Country(chat_tg_id=int(chat))
            logging.info(f'process died user {self.tg_id}: notify partner {partner_user.tg_id}')
            output[partner_user.tg_id] = 'Ваш партнер в стране %s, %s - умер...' % (country.name, self.name)

        # logging.info(f'process died user {user.tg_id}: 1')

        for child in childs_list:
            child_user = User.get(pk=child, age__gte=0, age__lte=100)
            if not child_user:
                continue
            logging.info(f'process died user {self.tg_id}: notify child {child_user.tg_id}')
            output[child_user.tg_id] = 'Ваш родитель, %s - умер...' % self.name

        # logging.info(f'process died user {user.tg_id}: 2')

        for parent in self.parents:
            if parent == "0":
                continue
            parent_user = User.get(pk=parent, age__gte=0, age__lte=100)
            if not parent_user:
                continue
            logging.info(f'process died user {self.tg_id}: notify parent {parent_user.tg_id}')
            output[parent_user.tg_id] = 'Ваше чадо, %s - умерло...' % self.name

        # logging.info(f'process died user {user.tg_id}: 3')

        return output

    async def marry(self, chat_tg_id: int, partner_tg_id: int):
        partner = Player(tg_id=partner_tg_id)
        if not partner:
            return 'Вы не можете вступить в брак с тем, кто не жив'
        if str(chat_tg_id) in self.partners:
            return 'Вы уже в браке в этой стране'
        if str(chat_tg_id) in partner.partners:
            return '%s уже в браке' % partner.name

        self.model.update(__raw__={'$set': {f'partners.{chat_tg_id}': partner.id}})
        partner.model.update(__raw__={'$set': {f'partners.{chat_tg_id}': self.id}})
        return ('Поздавляем <a href="tg://user?id=%d">%s</a> и <a href="tg://user?id=%d">%s</a> со свадьбой' %
                (self.tg_id, self.name, partner.tg_id, partner.name))

    async def divorce(self, chat_tg_id: int, partner: typing.Union[User, Player, int, ObjectId]):
        partner_arg_type = type(partner)

        if partner_arg_type == int:
            partner_model = User.get(tg_id=partner, age__gte=0, age__lte=100)
        elif partner_arg_type == Player:
            partner_model = partner.model
        elif partner_arg_type == ObjectId:
            partner_model = User.get(id=partner, age__gte=0, age__lte=100)
        elif partner_arg_type == User:
            partner_model = partner
        else:
            raise TypeError('partner arg type must be User, Player, int or ObjectId')

        self.model.unset_partner(chat_tg_id)
        partner_model.unset_partner(chat_tg_id)


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
