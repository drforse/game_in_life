from __future__ import annotations

from mongoengine import *
import datetime
import logging
import typing

from config import GAME_SPEED


class MyDocument:

    @classmethod
    def get(cls, **kwargs) -> typing.Union[User, None]:
        queryset_ = cls.objects(**kwargs)
        if queryset_:
            return queryset_[0]


class User(Document, MyDocument):
    tg_id = IntField(required=True)
    name = StringField(required=True)
    gender = StringField(required=True)  # male, female, transgender
    age = IntField(max_value=101, min_value=-1, default=0)
    chats = ListField(IntField())  # [chat_id]
    partners = DictField(default={})  # {chat_id: partner_id}
    lovers = DictField(default={})  # {chat_id: lover_id}
    childs = DictField(default={})  # {chat_id: List[child_id]}
    parents = ListField(default=[])

    def update_age(self, age: int = None):
        logging.info(f'update age of user {self.tg_id}')
        if age:
            logging.info(f'update age of user {self.tg_id}: exact age specified, setting age {age}')
            self.age = age
            self.save()
            return
        if self.age < 0 or self.age > 100:
            logging.info(f'update age of user {self.tg_id}: 0 > self.age {self.age} > 100')
            return
        creation_date = self.id.generation_time
        now = datetime.datetime.now(tz=creation_date.tzinfo)
        delta = now - creation_date
        age = int(delta.total_seconds() / GAME_SPEED)
        age = age if age < 101 else 101
        if self.age >= age:
            logging.info(f'update age of user {self.tg_id}: self.age {self.age} >= age {age}')
            return
        self.age = age
        self.save()
        logging.info(f'update age of user {self.tg_id}: {self.age} is new age!')
        if self.age > 100:
            logging.info(f'update age of user {self.tg_id}: died now')
            return 'died_now'

    def push_child(self, chat, child: int):
        self.update(__raw__={'$push': {f'childs.{chat}': child}})
        self.save()

    def set_partner(self, chat, partner: int):
        self.update(__raw__={'$set': {f'partners.{chat}': partner}})
        self.save()

    def unset_partner(self, chat):
        self.update(__raw__={'$unset': {f'partners.{chat}': {'$exists': True}}})
        self.save()

    def set_lover(self, chat, lover: int):
        self.update(__raw__={'$set': {f'lovers.{chat}': lover}})
        self.save()

    def unset_lover(self, chat):
        self.update(__raw__={'$unset': {f'lovers.{chat}': {'$exists': True}}})
        self.save()


class Group(Document, MyDocument):
    chat_tg_id = IntField(required=True)
    name = StringField(required=True)


class SexGifs(Document, MyDocument):
    type = StringField(required=True, unique=True)  # hetero, lesbian, gay, masturbate, universal
    gif_ids = ListField(required=True)

    @classmethod
    def push_gif(cls, sex_type: str, gif_id: str):
        model = cls.get(type=sex_type)
        if not model:
            cls(type=sex_type, gif_ids=[gif_id]).save()
            return
        model.update(push__gif_ids=gif_id)


class CumSexGifs(Document, MyDocument):
    type = StringField(required=True, unique=True)  # hetero, lesbian, gay, masturbate, universal
    gif_ids = ListField(required=True)

    @classmethod
    def push_gif(cls, sex_type: str, gif_id: str):
        model = cls.get(type=sex_type)
        if not model:
            cls(type=sex_type, gif_ids=[gif_id]).save()
            return
        model.update(push__gif_ids=gif_id)


__all__ = ['User',
           'Group',
           'SexGifs',
           'CumSexGifs']
