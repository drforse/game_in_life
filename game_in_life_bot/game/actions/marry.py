from .action import Action


class MarryAction(Action):

    async def complete(self, **kwargs):
        can_marry = await self.initiator.can_marry(self.chat_id, self.second_participant)
        if not can_marry['result']:
            self.add_text_message(self.initiator.cant_marry_reason_exaplanation[can_marry['reason']], 0)
            return

        async def foo(action_instance):
            action_instance.initiator.model.unset_lover(self.chat_id)
            action_instance.second_participant.model.unset_lover(self.chat_id)
            action_instance.initiator.model.set_partner(self.chat_id, self.second_participant.id)
            action_instance.second_participant.model.set_partner(self.chat_id, self.initiator.id)

        self.add_func_sub_action(foo(self), 0)
        self.add_text_message('{me} и {reply} заключили брак 💍', 0)
