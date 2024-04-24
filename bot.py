from src.data import Data, User
from src.staff.updates import Updater
from src.staff import utils
from src.staff import quiz
from src.sections import FullmemberSection, SecretarySection

from telebot import TeleBot, logger

import configparser
import logging, os

logger.setLevel(logging.INFO)

logger.info("Initializing settings")

config = configparser.ConfigParser()
config.read("Settings.ini")

logger.info("Settings read")

API_TOKEN = (
    os.environ.get("TOKEN", False)
    if os.environ.get("TOKEN", False)
    else config["TG"]["token"]
)
CONNECTION_STRING = (
    os.environ.get("DB", False)
    if os.environ.get("DB", False)
    else config["Mongo"]["db"]
)

bot = TeleBot(API_TOKEN, parse_mode="HTML")
data = Data(conn_string=CONNECTION_STRING, bot=bot)

logger.info("Connected to db")

updater = Updater()

full_section = FullmemberSection(data=data)
secretary_section = SecretarySection(data=data)


@bot.message_handler(commands=["start"])
def start_bot(message):
    user = updater.update_user_interaction_time(message)

    try:
        if user.username == data.config.secretary_user_name:
            user.set_secretary_status()
            secretary_section.send_start_menu(user)

        elif user.full_status:
            user.check_secretary_status()
            full_section.send_start_menu(user)

        else:
            user.check_secretary_status()
            bot.send_message(user.chat_id, "Привіт не-фул.\n\nЯк справи?")
            utils.send_random_quote(bot, user.chat_id)

    except Exception as e:
        print(f"Exception during start - {e}")


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user = updater.update_user_interaction_time(call.message)
    bot.clear_step_handler_by_chat_id(user.chat_id)
    section = call.data.split(";")[0]

    try:
        if section == "Full":
            full_section.process_callback(call=call, user=user)

        elif section == "Secretary":
            secretary_section.process_callback(call=call, user=user)

        elif section == "DELETE":
            utils.delete_message(bot=bot, call=call)

        elif section == "IGNORE":
            bot.answer_callback_query(call.id)

    except Exception as e:
        print(f"Exception during {section}.{call.data.split(';')[1]} btn tap - {e}")


@bot.message_handler(content_types=["text"])
def handle_text_buttons(message):
    user = updater.update_user_interaction_time(message)
    message_text = message.text

    try:

        if user.secretary_status and message_text == "СТОП":
            secretary_section.end_poll(user)

        else:
            utils.send_random_quote(
                bot, user.chat_id
            )  # answer user that it was invalid input (in utils.py maybe)

    except Exception as e:
        print(e)


if __name__ == "__main__":

    bot.polling(none_stop=True)
