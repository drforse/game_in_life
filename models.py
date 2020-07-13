import datetime
import logging
import typing

from mongoengine import *
from bson.objectid import ObjectId

from config import GAME_SPEED


class MyDocument:

    @classmethod
    def get(cls, **kwargs) -> typing.Union[
        'UserModel', 'GroupModel', 'SexGifsModel', 'CumSexGifsModel', 'DefaultUserpicsModel', Document, None]:
        """
        get object or None
        :param kwargs:
        :return:
        """
        queryset_ = cls.objects(**kwargs).order_by('-id')
        if queryset_:
            return queryset_[0]


class UserModel(Document, MyDocument):
    meta = {'collection': 'user'}
    tg_id = IntField(required=True)
    name = StringField(required=True)
    gender = StringField(required=True)  # male, female, transgender
    photo_id = StringField(default=None)
    main_currency_balance = FloatField(default=0.0)
    age = IntField(max_value=101, min_value=-1, default=0)
    chats = ListField(IntField())  # [chat_id]
    partners = DictField(default={})  # {chat_id: partner_id}
    lovers = DictField(default={})  # {chat_id: lover_id}
    childs = DictField(default={})  # {chat_id: List[child_id]}
    parents = ListField(default=[])
    satiety = FloatField(default=100, max_value=100, min_value=0, required=True)
    backpack = DictField(default={})

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

    def push_child(self, chat: int, child: ObjectId):
        self.update(__raw__={'$push': {f'childs.{chat}': child}})
        self.save()

    def set_partner(self, chat: int, partner: ObjectId):
        self.update(__raw__={'$set': {f'partners.{chat}': partner}})
        self.save()

    def unset_partner(self, chat: int):
        self.update(__raw__={'$unset': {f'partners.{chat}': {'$exists': True}}})
        self.save()

    def set_lover(self, chat: int, lover: ObjectId):
        self.update(__raw__={'$set': {f'lovers.{chat}': lover}})
        self.save()

    def unset_lover(self, chat: int):
        self.update(__raw__={'$unset': {f'lovers.{chat}': {'$exists': True}}})
        self.save()

    def inc_main_currency_balance(self, value: float):
        self.update(__raw__={'$inc': {'main_currency_balance': value}})
        self.save()


class ItemModel(Document, MyDocument):
    meta = {'collection': 'item'}
    name = StringField(required=True)
    price = FloatField(required=True)
    emoji = StringField()
    type = StringField(required=True)
    weight = FloatField(default=1.0, required=True)
    effects = ListField()


class GroupModel(Document, MyDocument):
    meta = {'collection': 'group'}
    chat_tg_id = IntField(required=True)
    name = StringField(required=True)


class SexGifsModel(Document, MyDocument):
    meta = {'collection': 'sex_gifs'}
    type = StringField(required=True, unique=True)  # hetero, lesbian, gay, masturbate, universal
    gif_ids = ListField(required=True)

    @classmethod
    def push_gif(cls, sex_type: str, gif_id: str, gif_unique_id: str):
        model = cls.get(type=sex_type)
        if not model:
            cls(type=sex_type, gif_ids=[{'file_id': gif_id,
                                         'file_unique_id': gif_unique_id}]).save()
            return
        model.update(push__gif_ids={'file_id': gif_id,
                                    'file_unique_id': gif_unique_id})

    @classmethod
    def pull_gif(cls, sex_type: str, gif_unique_id: str):
        model = cls.get(type=sex_type)
        if not model:
            return
        model.update(pull__gif_ids={'file_id': {'$exists': True},
                                    'file_unique_id': gif_unique_id})


class CumSexGifsModel(Document, MyDocument):
    """
    same as SexGifs, but different collection
    """
    meta = {'collection': 'cum_sex_gifs'}
    type = StringField(required=True, unique=True)  # hetero, lesbian, gay, masturbate, universal
    gif_ids = ListField(required=True)

    @classmethod
    def push_gif(cls, sex_type: str, gif_id: str, gif_unique_id: str):
        model = cls.get(type=sex_type)
        if not model:
            cls(type=sex_type, gif_ids=[{'file_id': gif_id,
                                         'file_unique_id': gif_unique_id}]).save()
            return
        model.update(push__gif_ids={'file_id': gif_id,
                                    'file_unique_id': gif_unique_id})

    @classmethod
    def pull_gif(cls, sex_type: str, gif_unique_id: str):
        model = cls.get(type=sex_type)
        if not model:
            return
        model.update(pull__gif_ids={'file_id': {'$exists': True},
                                    'file_unique_id': gif_unique_id})


class DefaultUserpicsModel(Document, MyDocument):
    photo_ids = ListField()
    meta = {'collection': 'default_userpics'}

    @classmethod
    def push_pic(cls, photo_id: str):
        model = cls.get()
        model.update(push__photo_ids=photo_id)

    @classmethod
    def pull_pic(cls, photo_id: str):
        model = cls.get()
        model.update(pull__photo_ids=photo_id)


__all__ = ['UserModel',
           'GroupModel',
           'SexGifsModel',
           'CumSexGifsModel',
           'DefaultUserpicsModel']
