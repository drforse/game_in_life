from pathlib import Path
import typing

from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram import types
from aiogram_oop_framework.core.project import Project, ProjectStructure
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from ..config import API_TOKEN
from .aiogram_middlwares import AuthMiddlware

PATH = Path(__file__).parent.parent.parent
PROJECT_NAME = "game_in_life_bot"
pr: Project = Project(PROJECT_NAME, PATH)
struc: ProjectStructure = ProjectStructure(pr)
struc.include('bot.views.inline')
struc.include('bot.views.callbacks')
struc.include('bot.views.messages.text')
struc.include('bot.views.messages.commands.user_commands')
struc.include('bot.views.messages.commands.dev_commands')
pr.structure = struc

PROJECT: Project = pr

AUTO_REGISTER_VIEWS = True


TELEGRAM_BOT_TOKEN: str = API_TOKEN

MIDDLEWARES: typing.List[BaseMiddleware.__class__] = [AuthMiddlware]

MEMORY_STORAGE = MemoryStorage()

PARSE_MODE = types.ParseMode.HTML
