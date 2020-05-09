import logging

from models import *


class Player:
    def __init__(self, tg_id: int = None, model: User = None):
        self.tg_id = tg_id
        model = model or User.get(tg_id=tg_id)
        if not model:
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

    async def create(self, name, gender, age, chats=(), parents=()):
        model = User(tg_id=self.tg_id, name=name, gender=gender, age=age, chats=list(chats), parents=list(parents))
        await self.update_from_db(model)
        model.save()
        return self

    async def update_from_db(self, model: User = None):
        model = model or User.get(pk=self.id)
        self.id = model.id
        self.name = model.name
        self.gender = model.gender
        self.age = model.age
        self.chats = model.chats
        self.parents = model.parents
        self.partners = model.partners
        self.childs = model.childs

    async def die(self, update_from_db=False):
        if update_from_db:
            await self.update_from_db()
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
            country = Country.get(chat_tg_id=int(chat))
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
