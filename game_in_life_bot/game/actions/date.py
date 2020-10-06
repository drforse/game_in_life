from .action import Action


class DateAction(Action):

    async def complete(self, **kwargs):
        can_date = await self.initiator.can_date(self.chat_id, self.second_participant)
        if not can_date['result']:
            self.add_text_message(self.initiator.cant_date_reason_exaplanation[can_date['reason']], 0)
            return

        self.initiator.model.set_lover(self.chat_id, self.second_participant.id)
        self.second_participant.model.set_lover(self.chat_id, self.initiator.id)
        text = '{me} и {reply} теперь встречаются'
        self.add_text_message(text, 0)
