from .section import Section
from .poll import PollSection
from .fullmember import FullmemberSection
from ..data import User, Data, Quiz, Poll
from ..staff import quiz

from telebot.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup


class SecretarySection(FullmemberSection):
    def __init__(self, data: Data):
        super().__init__(data)

        self.poll_section = PollSection(data)

    def process_callback(self, user: User, call: CallbackQuery):
        action = call.data.split(";")[1]

        if action == "StartMenu":
            self.send_start_menu(user, call)

        elif action == "NewPoll":
            self.create_new_poll(user)

        elif action == "PollList":
            self.send_poll_list_menu(user, call)

        elif action == "PollDetail":
            self.send_poll_detail_menu(user, call)

        elif action == "StartPoll":
            self.start_poll(user, call)

        elif action == "EndPoll":
            self.end_poll(user)

        elif action == "ShowPoll":
            self.show_poll_results(user)

        else:
            self.answer_in_development(call)
            return

        self.bot.answer_callback_query(call.id)

    def send_start_menu(self, user: User, call: CallbackQuery = None):

        text = "Привіт Секретар!"
        reply_markup = self._create_start_menu_markup()

        if call:
            self.send_message(call, text, reply_markup=reply_markup)
            return

        self.bot.send_message(
            user.chat_id,
            text=text,
            reply_markup=reply_markup,
        )

    def send_poll_list_menu(self, user: User, call: CallbackQuery = None):

        text = "Список непройдених голосувань."
        reply_markup = self._create_poll_list_markup()

        if call:
            self.send_message(
                call=call,
                text=text,
                reply_markup=reply_markup,
            )
            return

        self.bot.send_message(
            user.chat_id,
            text=text,
            reply_markup=reply_markup,
        )

    def send_poll_detail_menu(self, user: User, call: CallbackQuery):
        poll_id = call.data.split(";")[2]
        poll = Poll.objects.with_id(poll_id)

        markup = self._create_poll_detail_markup(poll_id)

        self.send_message(call, text=str(poll), reply_markup=markup)

    def create_new_poll(self, user: User):
        new_poll_quiz = self.data.new_poll_quiz

        quiz_iterator = iter(new_poll_quiz.questions)
        question = next(quiz_iterator)

        quiz.send_question(
            user,
            self.bot,
            question,
            quiz_iterator,
            save_func=self.poll_section.save_new_poll,
            final_func=self.send_poll_list_menu,
            container={},
            is_required=new_poll_quiz.is_required,
        )

    def start_poll(self, user: User, call: CallbackQuery):
        poll_id = call.data.split(";")[2]
        poll = Poll.objects.with_id(poll_id)

        if poll.is_completed:
            self.bot.send_message(user.chat_id, text="Це голосування вже завершено!")
            return
        self.poll_section.start_poll(user, poll)

    def show_poll_results(self, user: User):

        if self.poll_section.is_poll_active:
            self.bot.send_message(
                user.chat_id,
                text=self.poll_section._form_poll_message(),
            )
            return
        
        self.bot.send_message(
            user.chat_id,
            text="Голосування ще не почалось",
        )
         

    def end_poll(self, user: User):

        if self.poll_section.is_poll_active:
            self.poll_section.end_poll(update=True)
            return

        self.bot.send_message(
            user.chat_id, text="Голосування ще не розпочалось, а ти вже мене зупиняєш"
        )

    def _create_start_menu_markup(self) -> InlineKeyboardMarkup:

        markup = super()._create_start_menu_markup()

        poll_list_btn = InlineKeyboardButton(
            text="Список голосувань",
            callback_data=self.form_secretary_callback(action="PollList", edit=True),
        )

        full_list_btn = InlineKeyboardButton(
            text="Список фулів",
            callback_data=self.form_secretary_callback(action="FullList", new=True),
        )

        markup.add(poll_list_btn, full_list_btn)

        return markup

    def _create_poll_list_markup(self) -> InlineKeyboardMarkup:
        """Create buttons only for new Polls"""

        markup = InlineKeyboardMarkup()
        not_completed_polls = Poll.objects.filter(is_completed=False)

        for poll in not_completed_polls:
            poll_btn = InlineKeyboardButton(
                text=poll.name,
                callback_data=self.form_secretary_callback(
                    action="PollDetail", poll_id=poll.id, edit=True
                ),
            )
            markup.add(poll_btn)

        new_poll_btn = InlineKeyboardButton(
            text="➕ Нове голосування ➕",
            callback_data=self.form_secretary_callback(action="NewPoll", new=True),
        )

        back_btn = self.create_back_button(
            callback_data=self.form_secretary_callback(action="StartMenu", edit=True)
        )

        markup.add(new_poll_btn, back_btn)

        return markup

    def _create_poll_detail_markup(self, poll_id: str) -> InlineKeyboardMarkup:

        markup = InlineKeyboardMarkup()

        start_poll = InlineKeyboardButton(
            text="Розпочати голосування",
            callback_data=self.form_secretary_callback(
                action="StartPoll", poll_id=poll_id, edit=True
            ),
        )

        delete_poll = InlineKeyboardButton(
            text="Видалити голосування",
            callback_data=self.form_secretary_callback(
                action="DeletePoll", poll_id=poll_id, edit=True
            ),
        )

        end_poll = InlineKeyboardButton(
            text="Закінчити голосування",
            callback_data=self.form_secretary_callback(
                action="EndPoll", poll_id=poll_id, edit=True
            ),
        )

        show_poll = InlineKeyboardButton(
            text="Показати статус голосування",
            callback_data=self.form_secretary_callback(
                action="ShowPoll", poll_id=poll_id, edit=True
            ),
        )

        back_btn = self.create_back_button(
            callback_data=self.form_secretary_callback(action="PollList", edit=True)
        )

        markup.add(start_poll)
        markup.add(delete_poll)
        markup.add(show_poll)
        markup.add(end_poll)
        markup.add(back_btn)

        return markup
