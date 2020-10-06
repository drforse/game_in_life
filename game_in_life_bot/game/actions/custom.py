from .action import Action


class CustomAction(Action):
    async def complete(self, custom_data: str, **kwargs):
        self.add_from_string(custom_data)
