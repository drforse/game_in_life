from aiogram_oop_framework.views import CommandView


class UserCommandView(CommandView):
    needs_auth = True
    needs_reply_auth = True
    needs_satiety_level = 30
