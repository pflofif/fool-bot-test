from threading import Thread
from time import sleep

from .section import Section
from ..data import User, Data, Quiz, Poll
from ..staff import utils

from telebot.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Message,
)


class PollSection(Section):

    current_secretary: User
    current_poll: Poll

    current_users_polls: "List[[user: User, message_id: int]]"
    voted_users_list: "List"

    current_reply_markup: ReplyKeyboardMarkup

    is_poll_active: bool  # ?????

    def __init__(self, data: Data):
        super().__init__(data)
        self.is_poll_active = False

    def start_poll(self, secretary: User, poll: Poll):

        if self.is_poll_active:
            self.bot.send_message(secretary.chat_id, text="Голосування вже триває")
            return

        # initialize class values
        self.current_secretary = secretary
        self.current_poll = poll
        self.is_poll_active = True
        # self.current_poll.answers = list()
        self.current_users_polls = list()
        self.voted_users_list = list()
        self.current_reply_markup = self._create_poll_markup()

        # start Polling Thread
        poll_thread = Thread(target=self._start_poll)
        poll_thread.start()

    def end_poll(self, update: bool = False):
        self.is_poll_active = False

        if update:
            self._update_poll_messages()

        self.current_poll.randomize_answers_order()

        self._send_end_poll_massage_to_secretary()

        self.current_poll.complete()
        # self.current_poll.refresh()

        print("КІНЕЦЬ ГОЛОСУВАННЯ")

    def _send_end_poll_massage_to_secretary(self):

        self.bot.send_message(
            self.current_secretary.chat_id,
            text=self.current_poll.form_results(),
            reply_markup=ReplyKeyboardRemove(),
        )

    def _start_poll(self):

        self.current_users_list = self.current_poll.poll_members

        # register and send poll to every user
        for user in self.current_users_list:
            self._send_poll_to_user(user)

        self._update_poll_messages()

        # check if every user voted
        while self.is_poll_active:
            if len(self.voted_users_list) == len(self.current_users_polls):
                self.end_poll()

        print("Нарешті кінець!")

    def _send_poll_to_user(self, user: User):

        poll_message = self.bot.send_message(
            user.chat_id,
            text=self._form_poll_message(),
        )
        self.bot.send_message(
            chat_id=user.chat_id,
            text="Вибери варіант відповіді 🔽",
            reply_markup=self.current_reply_markup,
        )
        self.current_users_polls.append([user, poll_message.message_id])

        self.bot.register_next_step_handler_by_chat_id(
            user.chat_id, self._process_user_poll, user=user
        )

    def _process_user_poll(self, message: Message, **kwargs):
        def try_again(user: User):
            self.bot.send_message(
                message.chat.id, text="Вибери одну опцію з варіантів відповідей!"
            )

            self.bot.register_next_step_handler_by_chat_id(
                message.chat.id, self._process_user_poll, user=user
            )

        user = kwargs["user"]

        if message.content_type != "text":
            try_again(user)
            return

        user_answer = message.text

        if user_answer not in self.current_poll.answer_options:
            try_again(user)
            return

        self.current_poll.answers += [user_answer]
        self.current_poll.save()

        self.voted_users_list += [user]

        user.polls_participated += 1
        user.save()

        self.bot.send_message(
            user.chat_id,
            text="Твій голос прийнято!",
            reply_markup=ReplyKeyboardRemove(),
        )
        self._update_poll_messages()

    def _form_poll_message(self) -> str:
        poll_status = (
            "Голосування триває..." if self.is_poll_active else "Голосування завершено!"
        )

        return (
            f"<b>{self.current_poll.name}</b>\n"
            f"<i>{self.current_poll.question}</i>\n\n"
            f"<b>Статус голосування фулів:</b>\n{self._get_users_vote_statuses()}\n"
            f"<b>{poll_status}</b>"
        )

    def _create_poll_markup(self) -> ReplyKeyboardMarkup:
        markup = ReplyKeyboardMarkup()

        for row in utils.reply_keyboard_columns_generator(
            btn_names_list=self.current_poll.answer_options
        ):
            markup.add(*row)

        return markup

    def _update_poll_messages(self):

        counter = 0
        for user, message_id in self.current_users_polls:
            updated_message_text = self._form_poll_message()

            # if user deleted his message (user - debil) - send new
            while counter < 3:
                try:
                    self.bot.edit_message_text(
                        text=updated_message_text,
                        chat_id=user.chat_id,
                        message_id=message_id,
                    )
                    counter = 3

                except:
                    print(
                        f"Error occured when editing voting results for {user.username}. Sleeping for 0.5 seconds"
                    )
                    sleep(0.5)

                counter += 1

            counter = 0

    def _get_users_vote_statuses(self) -> str:
        vote_statuses = str()

        for user_poll in self.current_users_polls:
            user = user_poll[0]
            user_poll_msg_id = user_poll[1]

            status = "✅" if user in self.voted_users_list else "❌"
            vote_statuses += f"{user.name} (@{user.username}) - {status}\n"

        return vote_statuses

    def _get_users_by_usernames(self, username_list: "List"):
        users_list = list()

        for username in username_list:
            user = User.objects.filter(username=username.strip().split("@")[1]).first()

            if user is None:
                return username

            users_list.append(user)

        return users_list

    def save_new_poll(self, user: User, container: "Dict"):

        try:
            answer_options = container["answer_options"].split("\n")
            answer_options += ["БЛАНК"]

            poll_members = container["poll_members"].split("\n")
            poll_members = self._get_users_by_usernames(poll_members)

            if isinstance(poll_members, str):
                self.bot.send_message(
                    user.chat_id,
                    text=f"А ні, я тебе надурив(\n\nКористувача з ніком {poll_members} не зареєстрований в боті або він змінив свій юзернейм.\n\n<b>Голосування не було додано</b>",
                )
                return

            new_poll = Poll(
                name=container["poll_name"],
                question=container["question"],
                answer_options=answer_options,
                poll_members=poll_members,
                creation_date=utils.get_now(),
            )

            new_poll.save()

            print(f"New poll {container['poll_name']} is succesfully saved")

        except Exception as e:
            print(
                f"New poll {container['poll_name']} IS NOT succesfully saved due to {e}"
            )
