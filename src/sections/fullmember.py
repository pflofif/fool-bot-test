from .section import Section
from ..data import User, Data

from telebot.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup


class FullmemberSection(Section):
    def __init__(self, data: Data):
        super().__init__(data)

    def process_callback(self, user: User, call: CallbackQuery):
        action = call.data.split(";")[1]

        if action == "PollHistory":
            pass

        else:
            pass

        self.bot.answer_callback_query(call.id)

    def send_start_menu(self, user: User):

        self.bot.send_message(
            user.chat_id,
            text="Привіт Фул!",
            reply_markup=self._create_start_menu_markup(),
        )

    def _create_start_menu_markup(self) -> InlineKeyboardMarkup:

        markup = InlineKeyboardMarkup()

        poll_history_btn = InlineKeyboardButton(
            text="Історія голосувань",
            callback_data=self.form_full_callback(action="PollHistory", edit=True),
        )

        markup.add(poll_history_btn)

        return InlineKeyboardMarkup()
