from pathlib import Path
import typing

from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram import types
from aiogram_oop_framework.core.project import Project, ProjectStructure
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import API_TOKEN
from .aiogram_middlwares import AuthMiddlware

PATH = Path.cwd()
PROJECT_NAME = "bot"
pr: Project = Project(PROJECT_NAME, PATH)
struc: ProjectStructure = ProjectStructure(pr)
struc.include('views.inline')
struc.include('views.callbacks')
struc.include('views.messages.text')
struc.include('views.messages.commands.user_commands')
struc.include('views.messages.commands.dev_commands')
pr.structure = struc

PROJECT: Project = pr

AUTO_REGISTER_VIEWS = True


TELEGRAM_BOT_TOKEN: str = API_TOKEN

MIDDLEWARES: typing.List[BaseMiddleware.__class__] = [AuthMiddlware]

MEMORY_STORAGE = MemoryStorage()

PARSE_MODE = types.ParseMode.HTML
