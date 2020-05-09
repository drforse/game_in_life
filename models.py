from mongoengine import *
import datetime
import logging

from config import game_speed


class User(Document):
    tg_id = IntField(required=True)
    name = StringField(required=True, max_length=50)
    gender = StringField(required=True, max_length=11)  # male, female, transgender
    age = IntField(max_value=101, min_value=-1, default=0)
    chats = ListField(IntField())  # [chat_id]
    partners = DictField(default={})  # {chat_id: partner_id}
    childs = DictField(default={})  # {chat_id: List[child_id]}
    parents = ListField(default=[])

    def update_age(self):
        logging.info(f'update age of user {self.tg_id}')
        if self.age < 0 or self.age > 100:
            logging.info(f'update age of user {self.tg_id}: 0 > age {age} > 100')
            return
        creation_date = self.pk.generation_time
        now = datetime.datetime.now(tz=creation_date.tzinfo)
        delta = now - creation_date
        age = int(delta.total_seconds() / game_speed)
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

    def push_child(self, chat, child):
        self.update(__raw__={'$push': {f'childs.{chat}': child}})
        self.save()


class Country(Document):
    chat_tg_id = IntField(required=True)
    name = StringField(required=True, max_length=50)


__all__ = ['User',
           'Country']
