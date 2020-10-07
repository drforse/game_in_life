import asyncio
from typing import Union, Callable, List, Awaitable

from aiogram import Bot
from aiogram.types.base import InputFile

from game_in_life_bot.game.utils import pairwise


class SubAction:
    def __init__(self, **kwargs):
        self.chat_id: int = None
        self.initiator: 'Player' = None
        self.second_participant: 'Player' = None
        for k, v in kwargs.items():
            setattr(self, k, v)

    def do(self, *args, **kwargs):
        raise NotImplementedError


class TextSubAction(SubAction):
    def __init__(self,
                 text: str,
                 delay: float,
                 chat_id: int,
                 initiator: 'Player',
                 second_participant: 'Player'):
        self.text: str = None
        self.delay: float = None
        kwargs = locals()
        del kwargs['self']
        super().__init__(**kwargs)
        self.sent_message = None

    async def do(self, *args, bot: Bot, last_action=None, **kwargs):
        text = ""
        if isinstance(last_action, TextSubAction):
            text = last_action.sent_message.text + "\n"
        append = self.text.replace('{me}', self.initiator.name).replace('{reply}', self.second_participant.name)
        text += append
        if len(text + append) < 3000 and text != append:
            self.sent_message = await last_action.sent_message.edit_text(text)
        else:
            self.sent_message = await bot.send_message(self.chat_id, append)
        await asyncio.sleep(self.delay)
        return self


class GifSubAction(SubAction):
    def __init__(self,
                 gif: Union[str, InputFile],
                 delay: float,
                 chat_id: int,
                 initiator: 'Player',
                 second_participant: 'Player'):
        self.gif: Union[str, InputFile] = None
        self.delay: float = None
        kwargs = locals()
        del kwargs['self']
        super().__init__(**kwargs)
        self.sent_message = None

    async def do(self, *args, bot: Bot, **kwargs):
        self.sent_message = await bot.send_animation(self.chat_id, self.gif)
        await asyncio.sleep(self.delay)
        return self


class DelaySubAction(SubAction):
    def __init__(self, delay: int):
        self.delay = delay

    async def do(self, *args, **kwargs):
        await asyncio.sleep(delay=self.delay)


class FuncSubAction(SubAction):
    def __init__(self, func: Awaitable, delay: int, *args, **kwargs):
        self.func: Awaitable = func
        self.delay: int = delay
        self.args = args
        self.kwargs = kwargs

    async def do(self, *args, **kwargs):
        return await self.func


class Action:
    def __init__(self,
                 used_satiety: float,
                 initiator: 'Player',
                 second_participant: 'Player',
                 chat_id: int):
        self.used_satiety: float = used_satiety
        self.chat_id: int = chat_id
        self.initiator: 'Player' = initiator
        self.second_participant: 'Player' = second_participant
        self.actions: List[SubAction] = []
        self.finished: bool = False

    def get_text_sub_action(self, text: str, delay: int):
        return TextSubAction(text, delay, self.chat_id, self.initiator, self.second_participant)

    def get_gif_sub_action(self, gif: Union[str, InputFile], delay: int):
        return GifSubAction(gif, delay, self.chat_id, self.initiator, self.second_participant)

    def get_func_sub_action(self, func: Awaitable, delay: int):
        return FuncSubAction(
            func, delay, chat_id=self.chat_id, initiator=self.initiator,
            second_participant=self.second_participant)

    @staticmethod
    def get_delay_sub_action(delay):
        return DelaySubAction(delay=delay)

    def add_text_message(self, text: str, delay: int):
        self.actions.append(self.get_text_sub_action(text, delay))

    def add_gif_message(self, gif: Union[str, InputFile], delay: int):
        self.actions.append(self.get_gif_sub_action(gif, delay))

    def add_func_sub_action(self, func: Awaitable, delay: int):
        self.actions.append(self.get_func_sub_action(func, delay))

    def add_delay_sub_action(self, delay):
        self.actions.append(self.get_delay_sub_action(delay))

    def add_from_string(self, s):
        self.actions += self.parse_from_string(s)

    def parse_from_string(self, s):
        actions = []
        split = s.split('|')
        for text, delay in pairwise(split):
            actions.append(TextSubAction(
                text, int(delay), self.chat_id, self.initiator, self.second_participant))
        actions.append(TextSubAction(
            split[-1], 0, self.chat_id, self.initiator, self.second_participant))
        return actions

    def add_actions(self, actions: Union[list, SubAction]):
        if isinstance(actions, list):
            self.actions += actions
        else:
            self.actions += [actions]

    async def do(self, *args, **kwargs):
        results = []

        result = await self.actions[0].do(*args, **kwargs)
        results.append(result)
        if len(self.actions) > 1:
            for action in self.actions[1:]:
                result = await action.do(*args, **kwargs, last_action=result)
                results.append(result)

        for participant in [self.initiator, self.second_participant]:
            if not participant.alive:
                continue
            participant.satiety -= self.used_satiety
            participant.model.satiety = participant.satiety
            participant.model.save()
            if self.initiator.id == self.second_participant.id:
                break
        self.finished = True
        return results
