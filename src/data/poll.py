import mongoengine as me
from enum import Enum
from ..data import User
from random import shuffle


class PollType(Enum):
    ONE_ANSWER = "One answer"
    MULTIPLE_ANSWER = "Multiple answer"


class Poll(me.Document):
    name = me.StringField(required=True)
    question = me.StringField(required=True)
    poll_type = me.StringField(required=True, default=PollType.ONE_ANSWER.value)
    answer_options = me.ListField(field=me.StringField(), required=True)
    poll_members = me.ListField(field=me.ReferenceField(User), required=True)

    answers = me.ListField(default=list())
    creation_date = me.DateTimeField(required=True)
    completion_date = me.DateTimeField()
    is_completed = me.BooleanField(default=False)

    def __str__(self):
        poll_members = [f"@{user.username}" for user in self.poll_members]

        return (
            f"<b>{self.name}</b>\n"
            f"<i>{self.question}</i>\n\n"
            f"Тип голосування - {self.poll_type}\n\n"
            f"Варіанти відповідей - {self.answer_options}'\n\n"
            f"Фули які беруть участь у голосуванні ({len(self.poll_members)}) - {poll_members}\n\n"
            f"Дата створення голосування - {self.creation_date}"
        )

    def randomize_answers_order(self):
        """Make answers order random to prevent checking votes owners"""
        shuffle(list(self.answers))
        self.save()

    def complete(self):
        self.is_completed = True
        self.save()

    def refresh(self):
        self.answers = list()
        self.save()

    def form_results(self):
        result_dict = {f"{answer}": 0 for answer in self.answer_options}

        for answer in self.answers:
            result_dict[answer] += 1

        results_str = (
            f"<b>{self.name}</b>\n"
            f"<i>{self.question}</i>\n\n"
            "<b>Результати голосувань</b>\n\n"
        )

        if(len(self.answers) == 0):
            return "Голосування закінчено\n\n0 голосів, клас"
        
        for key, value in result_dict.items():
            results_str += f"{key} - {value/len(self.answers)*100:.2f}% ({value})\n"

        return results_str
