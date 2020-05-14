from __future__ import annotations

import logging
import random
import typing
import asyncio
from mongoengine.queryset.visitor import Q

from models import *


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
                                     'is_dating': 'Вы не можете встречаться с тем, кто уже состоит '
                                                  'в романтических отношениях',
                                     'married': 'Вы в браке',
                                     'lover_married': 'Вы не можете встречаться с тем, кто состоит в браке',
                                     'lover_dating': 'Этот человек с кем-то уже встречается'}

    gender_emoji_reference = {'male': '♂️', 'female': '♀️', 'transgender': '♂️♀️'}

    def __init__(self, tg_id: int = None, model: User = None):
        self.tg_id = tg_id
        self.exists = False
        self.name = None
        self.gender = None
        self.age = None
        self.chats = None
        self.parents = None
        self.partners = None
        self.lovers = None
        self.childs = None
        self.alive = None
        self.in_born_queue = None
        self.model = model
        self.update_from_db(model)

    async def create(self, name, gender, age, chats=(), parents=()) -> Player:
        model = User(tg_id=self.tg_id, name=name, gender=gender, age=age,
                     chats=list(chats), parents=list(parents))
        model.save()
        self.update_from_db(model)
        return self

    def update_from_db(self, model: User = None):
        model = model if model else User.get(tg_id=self.tg_id)
        self.model = model
        if not model:
            self.exists = False
            return
        self.tg_id = model.tg_id
        self.name = model.name
        self.gender = model.gender
        self.age = model.age
        self.chats = model.chats
        self.parents = model.parents
        self.partners = model.partners
        self.lovers = model.lovers
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

        logging.info(f'process died user {self.tg_id}')

        output = await self.notify_partners_about_death()
        output.update((await self.notify_childs_about_death()))
        output.update((await self.notify_parents_about_death()))

        logging.info(f'process died user {self.tg_id}: finished')

        return output

    async def notify_partners_about_death(self) -> dict:
        output = {}
        for chat in self.partners:
            partner_player = Player(tg_id=self.partners[chat])
            await partner_player.divorce(chat, partner_player)
            if not partner_player.alive:
                continue
            country = Country(chat_tg_id=int(chat))
            logging.info(f'process died user {self.tg_id}: notify partner {partner_player.tg_id}')
            output[partner_player.tg_id] = 'Ваш партнер в стране %s, %s - умер...' % (country.name, self.name)
        return output

    async def notify_childs_about_death(self) -> dict:
        output = {}
        childs = []
        for chat in self.childs:
            childs = self.childs.get(chat, [])
            childs += childs
        for child_id in childs:
            child_user = Player(tg_id=child_id)
            if not child_user.alive:
                continue
            logging.info(f'process died user {self.tg_id}: notify child {child_id}')
            output[child_id] = 'Ваш родитель, %s - умер...' % self.name
        return output

    async def notify_parents_about_death(self) -> dict:
        output = {}
        for parent_id in self.parents:
            if parent_id == "0":
                continue
            parent_player = Player(tg_id=parent_id)
            if not parent_player.alive:
                continue
            logging.info(f'process died user {self.tg_id}: notify parent {parent_player.tg_id}')
            output[parent_player.tg_id] = 'Ваше чадо, %s - умерло...' % self.name
        return output

    async def marry(self, chat_tg_id: int, partner_tg_id: int):
        partner = Player(tg_id=partner_tg_id)

        can_marry = await self.can_marry(chat_tg_id, partner)
        if not can_marry['result']:
            return self.cant_marry_reason_exaplanation[can_marry['reason']]

        self.model.set_partner(chat_tg_id, partner.tg_id)  # update(__raw__={'$set': {f'partners.{chat_tg_id}': partner.tg_id}})
        partner.model.set_partner(chat_tg_id, self.tg_id)  # update(__raw__={'$set': {f'partners.{chat_tg_id}': self.tg_id}})
        self.model.unset_lover(chat_tg_id)
        partner.model.unset_lover(chat_tg_id)
        return ('Поздавляем <a href="tg://user?id=%d">%s</a> и <a href="tg://user?id=%d">%s</a> со свадьбой' %
                (self.tg_id, self.name, partner.tg_id, partner.name))

    async def date(self, chat_tg_id: int, lover_tg_id: int):
        lover = Player(tg_id=lover_tg_id)

        can_date = await self.can_date(chat_tg_id, lover)
        if not can_date['result']:
            return self.cant_date_reason_exaplanation[can_date['reason']]

        self.model.set_lover(chat_tg_id, lover.tg_id)  # update(__raw__={'$set': {f'lovers.{chat_tg_id}': lover.tg_id}})
        lover.model.set_lover(chat_tg_id, self.tg_id)  # update(__raw__={'$set': {f'lovers.{chat_tg_id}': self.tg_id}})
        return ('<a href="tg://user?id=%d">%s</a> и <a href="tg://user?id=%d">%s</a> теперь встречаются' %
                (self.tg_id, self.name, lover.tg_id, lover.name))

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
        if self.lovers.get(str(chat_tg_id), partner.tg_id) != partner.tg_id:
            return {'result': False, 'reason': 'is_dating_another_person'}
        if partner.lovers.get(str(chat_tg_id), self.tg_id) != self.tg_id:
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
        if self.tg_id == lover.tg_id:
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

    async def divorce(self, chat_tg_id: int, partner: typing.Union[User, Player, int] = None):
        if partner:
            partner_model = await self.resolve_user(partner, 'User')
        else:
            partner_model = User(tg_id=self.model.partners[str(chat_tg_id)])
        self.model.unset_partner(chat_tg_id)
        partner_model.unset_partner(chat_tg_id)

    async def break_up(self, chat_tg_id: int, lover: typing.Union[User, Player, int] = None):
        if lover:
            lover_model = await self.resolve_user(lover, 'User')
        else:
            lover_model = User(tg_id=self.model.lovers[str(chat_tg_id)])
        self.model.unset_lover(chat_tg_id)
        lover_model.unset_lover(chat_tg_id)

    async def fuck(self, chat_id, partner: typing.Union[User, Player, int], delay: int = 300):
        partner = await self.resolve_user(partner, 'Player')

        sex_types = await self.get_sex_types(partner)
        sex_type = sex_types['main']
        universal_sex_type = sex_types['universal']

        if sex_type.startswith('masturbate'):
            verb_form = 'кончил' if self.gender == 'male' else 'кончила' if self.gender == 'female' else 'кончил(а)'
            start_message = '<a href="tg://user?id=%d">%s</a> дрочит.' % (self.tg_id, self.name)
            end_message = '<a href="tg://user?id=%d">%s</a> %s.' % (self.tg_id, self.name, verb_form)
        else:
            start_message = '<a href="tg://user?id=%d">%s</a> и <a href="tg://user?id=%d">%s</a> пошли трахаться :3' %\
                            (self.tg_id, self.name, partner.tg_id, partner.name)
            end_message = '<a href="tg://user?id=%d">%s</a> и <a href="tg://user?id=%d">%s</a> закончили трахаться' % \
                          (self.tg_id, self.name, partner.tg_id, partner.name)

        yield {'content_type': 'text', 'content': start_message}

        possible_gifs = await self.get_possible_sex_gifs(sex_type, universal_sex_type)

        if possible_gifs:
            yield {'content_type': 'animation', 'content': random.choice(possible_gifs)}
        await asyncio.sleep(delay)

        child = await self.get_child_and_parents(chat_id, partner)
        if child['child']:
            mother = child['mother']
            father = child['father']
            child = child['child']
            end_message += ('\n\n<a href="tg://user?id=%d">%s</a> забеременела и родила '
                            '<a href="tg://user?id=%d">%s</a>' % (mother.tg_id, mother.name, child.tg_id,
                                                                  child.name)
                            )
            child = Player(model=child)
            await Player.born(child, mother, father, chat_id)

        yield {'content_type': 'text', 'content': end_message}

        possible_gifs = await self.get_possible_cum_sex_gifs(sex_type, universal_sex_type)
        if possible_gifs:
            yield {'content_type': 'animation', 'content': random.choice(possible_gifs)}

    async def get_child_and_parents(self, chat_id: int,
                                    partner: Player) -> typing.Dict[str, typing.Union[User, Player]]:
        child = None
        female = self if self.gender == 'female' else partner if partner.gender == 'female' else None
        male = self if self.gender == 'male' else partner if partner.gender == 'male' else None
        if male and female and female.age >= 12:

            country = Country(chat_id)
            childs_queue = await country.get_childs_queue()
            if childs_queue:
                child = random.choice(childs_queue)
        return {'child': child, 'mother': female, 'father': male}

    async def get_sex_types(self, partner: Player) -> dict:
        if self.tg_id == partner.tg_id:
            if self.gender == 'male':
                sex_type = 'masturbate_male'
            elif self.gender == 'female':
                sex_type = 'masturbate_female'
            else:
                sex_type = 'masturbate_transgender'
        elif self.gender == 'male' and partner.gender == 'female':
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

        return {'main': sex_type, 'universal': universal_sex_type}

    @staticmethod
    async def get_possible_sex_gifs(sex_type: str, universal_sex_type: str) -> list:
        possible_gif_models = SexGifs.objects(Q(type=sex_type) | Q(type=universal_sex_type))
        possible_gifs = []
        for model in possible_gif_models:
            possible_gifs += model.gif_ids
        return possible_gifs

    @staticmethod
    async def get_possible_cum_sex_gifs(sex_type: str, universal_sex_type: str) -> list:
        possible_gif_models = CumSexGifs.objects(Q(type=sex_type) | Q(type=universal_sex_type))
        possible_gifs = []
        for model in possible_gif_models:
            possible_gifs += model.gif_ids
        return possible_gifs

    async def born(self, mother: Player, father: Player, chat: typing.Union[Country, int]):
        if isinstance(chat, Country):
            chat = Group.chat_tg_id
        self.model.delete()
        child = Player(tg_id=self.tg_id)
        child = await child.create(name=self.name, gender=self.gender, age=0,
                                   chats=self.chats, parents=[mother.tg_id, father.tg_id])
        mother.model.push_child(chat, child.tg_id)
        father.model.push_child(chat, child.tg_id)

    @staticmethod
    async def resolve_user(user: typing.Union[User, Player, int], result_type: str = 'Player'):
        user_type = type(user)
        if user_type == Player:
            if result_type == 'Player':
                return user
            model = user.model
        elif user_type == User:
            model = user
        elif user_type == int:
            model = User.get(tg_id=user, age__gte=0, age__lte=100)
        else:
            raise TypeError('partner arg type must be User, Player or int')

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


class Eva:
    gender = 'female'
    name = 'Ева'


class Adam:
    gender = 'male'
    name = 'Адам'
