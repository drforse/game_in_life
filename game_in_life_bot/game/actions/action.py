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

    async def do(self, bot: Bot):
        text = self.text.replace('{me}', self.initiator.name).replace('{reply}', self.second_participant.name)
        await bot.send_message(self.chat_id, text)
        await asyncio.sleep(self.delay)


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

    async def do(self, bot: Bot):
        await bot.send_animation(self.chat_id, self.gif)
        await asyncio.sleep(self.delay)


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
        await self.func


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
        for action in self.actions:
            await action.do(*args, **kwargs)
        for participant in [self.initiator, self.second_participant]:
            participant.satiety -= self.used_satiety
            participant.model.satiety = participant.satiety
            participant.model.save()
            if self.initiator.id == self.second_participant.id:
                break
        self.finished = True
