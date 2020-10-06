from .action import Action


class MarryAction(Action):

    async def complete(self, **kwargs):
        can_marry = await self.initiator.can_marry(self.chat_id, self.second_participant)
        if not can_marry['result']:
            self.add_text_message(self.initiator.cant_marry_reason_exaplanation[can_marry['reason']], 0)
            return

        self.initiator.model.unset_lover(self.chat_id)
        self.second_participant.model.unset_lover(self.chat_id)
        self.initiator.model.set_partner(self.chat_id, self.second_participant.id)
        self.second_participant.model.set_partner(self.chat_id, self.initiator.id)
        self.add_text_message('{me} и {reply}', 0)
