from telebot.types import Message, KeyboardButton, CallbackQuery
from telebot import TeleBot

import requests
import tempfile
import shutil
import os
import time
from datetime import datetime, timezone

import requests


def send_random_quote(bot: TeleBot, chat_id):
    quote = requests.get("https://api.quotable.io/random?tags=famous-quotes").json()

    author = quote["author"]
    content = quote["content"]

    bot.send_message(
        chat_id,
        text=(f"<b>{author}</b>\n\n" f"{content}\n\n" f"<b>Пиши + якщо хочеш ще</b>"),
    )


def reply_keyboard_columns_generator(btn_names_list: list, col=2):
    row = []

    for index, btn_name in enumerate(btn_names_list, 1):
        row += [KeyboardButton(btn_name)]

        if index % col == 0:
            yield row
            row = []

    if row:
        yield row


def delete_message(bot: TeleBot, call: CallbackQuery):
    chat_id = call.message.chat_id
    message_id = call.message.message_id

    try:
        bot.delete_message(chat_id, message_id)

    except:
        bot.answer_callback_query(call.id, text="Щоб продовжити натискай на /start")


def time_check(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        rest = func(*args, **kwargs)
        end = time.time()
        print(f"Час виконання {(end - start):.4} секунд")
        return rest

    return wrapper


def get_now() -> datetime:
    return datetime.now(tz=timezone.utc)
