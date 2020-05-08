from mongoengine import *
import datetime

from config import game_speed


class User(Document):
    tg_id = IntField(required=True)
    name = StringField(required=True, max_length=50)
    gender = StringField(required=True, max_length=11)  # male, female, transgender
    age = IntField(max_value=101, min_value=-1, default=0)
    chats = ListField(IntField())  # [chat_id]
    partners = DictField(default={})  # {chat_id: partner_id}
    childs = DictField(default={})  # {chat_id: List[child_id]}
    parents = ListField(default={})

    def update_age(self):
        if self.age < 0 or self.age > 100:
            return
        creation_date = self.pk.generation_date
        now = datetime.datetime.now()
        delta = now - creation_date
        age = int(delta.hour / game_speed)
        if self.age == age:
            return
        self.age = age if age <= 100 else 101
        self.save()
        if self.age > 100:
            return 'died_now'


class Country(Document):
    chat_tg_id = IntField(required=True)
    name = StringField(required=True, max_length=50)
