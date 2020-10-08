from .action import Action


class DateAction(Action):

    async def complete(self, **kwargs):
        can_date = await self.initiator.can_date(self.chat_id, self.second_participant)
        if not can_date['result']:
            self.add_text_message(self.initiator.cant_date_reason_exaplanation[can_date['reason']], 0)
            return

        async def foo(action_instance):
            action_instance.initiator.model.set_lover(self.chat_id, self.second_participant.id)
            action_instance.second_participant.model.set_lover(self.chat_id, self.initiator.id)

        self.add_func_sub_action(foo(self), 0)
        text = '{me} и {reply} теперь встречаются'
        self.add_text_message(text, 0)
