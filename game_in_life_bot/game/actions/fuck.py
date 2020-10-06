import random
from pathlib import Path

from .action import Action


class FuckAction(Action):

    async def complete(self, delay: int = 300, custom_data: str = None, **kwargs):
        if not self.second_participant.alive:
            file_path = Path(__file__).parent / Path(f'texts/fuck/dead/{self.initiator.gender}_with/{self.second_participant.gender}/0.txt')
            if not file_path.exists():
                file_path = Path(__file__).parent / Path(f'texts/fuck/dead/universal/0.txt')
            else:
                delay = 0
            with open(file_path, encoding='utf-8') as f:
                custom_data = f.read()

        custom_actions = []
        if custom_data:
            custom_actions = self.parse_from_string(custom_data)
            self.add_actions(custom_actions[0:1])
            last_action = custom_actions[-1]
        elif self.initiator.id == self.second_participant.id:
            verb_form = 'кончил' if self.initiator.gender == 'male' else 'кончила' if self.initiator.gender == 'female' else 'кончил(а)'
            self.add_text_message('{me} дрочит.', 0)
            last_action = self.get_text_sub_action('{me} %s.' % verb_form, 0)
        else:
            self.add_text_message('{me} и {reply} пошли трахаться :3', 0)
            last_action = self.get_text_sub_action('{me} и {reply} закончили трахаться', 0)

        sex_types = await self.initiator.get_sex_types(self.second_participant)
        sex_type = sex_types['main']
        universal_sex_type = sex_types['universal']
        possible_gifs = await self.initiator.get_possible_sex_gifs(sex_type, universal_sex_type)

        if possible_gifs:
            self.add_gif_message(random.choice(possible_gifs), 0)
        self.add_delay_sub_action(delay)
        if len(custom_actions) > 1:
            self.add_actions(custom_actions[1:-1])

        child = await self.initiator.get_child_and_parents(self.chat_id, self.second_participant)
        if child['child']:
            mother = child['mother']
            father = child['father']
            child = child['child']
            last_action.text += ('\n\n<a href="tg://user?id=%d">%s</a> забеременела и родила '
                                 '<a href="tg://user?id=%d">%s</a>' % (mother.tg_id, mother.name, child.tg_id,
                                                                       child.name))
            from game_in_life_bot.game.types import Player
            child = Player(model=child)
            self.add_func_sub_action(child.born(mother, father, self.chat_id), 0)
            self.used_satiety += 10

        self.add_actions(last_action)

        possible_gifs = await self.initiator.get_possible_cum_sex_gifs(sex_type, universal_sex_type)
        if possible_gifs:
            self.add_gif_message(random.choice(possible_gifs), 0)
