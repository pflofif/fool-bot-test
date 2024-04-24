from telebot import TeleBot
from telegraph import Telegraph
import mongoengine as me
from datetime import datetime, timezone

from ..data import Config
from .quiz import Quiz, Question

import string
import random


class Data:

    TEST_PHOTO = "https://pentagram-production.imgix.net/2f4d7366-e44e-4997-9c62-cf7af633aadc/LH_TMF_03-still.jpg"

    def __init__(self, conn_string: str, bot: TeleBot):
        self.bot = bot

        me.connect(host=conn_string, ssl=True, ssl_cert_reqs='CERT_NONE')
        print("connection success ")

        self.create_system_tables()

    @property
    def config(self) -> Config:
        return Config.objects.first()

    @property
    def starting_quiz(self) -> Quiz:
        return Quiz.objects.filter(name="StartQuiz").first()

    @property
    def new_poll_quiz(self) -> Quiz:
        return Quiz.objects.filter(name="NewPollQuiz").first()

    def create_system_tables(self):

        if Config.objects.count() == 0:
            self._create_config_table()

        self._create_quizes()

    def _create_config_table(self):
        config = Config()

        config.save()

        print("Config table has been created.")

    def _create_quizes(self):
        if Quiz.objects.filter(name="StartQuiz").count() == 0:
            self._add_start_quiz()

        if Quiz.objects.filter(name="NewPollQuiz").count() == 0:
            self._add_new_poll_quiz()

    def _add_start_quiz(self):

        quiz = Quiz(name="StartQuiz", is_required=True)

        q_name_surname = Question(
            name="name_surname",
            message="Введи своє ім'я та прізвище на англійській мові",
            regex="/^[a-z ,.'-]+$/i",
            correct_answer_message="Перевірка на фула 1/3",
            wrong_answer_message="Потрібно використовувати лише літери англійського алфавіту!",
        )

        q_contact = Question(
            name="contact",
            message="Обміняємося контактами?",
            buttons=["Тримай!"],
            input_type="contact",
            correct_answer_message="Перевірка на фула 1/3",
            wrong_answer_message="Надішли, будь ласка, свій контакт 🤡",
        )

        q_email = Question(
            name="email",
            message="Наостанок, вкажи адресу своєї поштової скриньки.",
            regex="^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$",
            correct_answer_message="Перевірка на фула завершена...",
            wrong_answer_message="Введи, будь ласка, електронну адресу 🤡",
        )

        quiz.questions = [
            q_name_surname,
            q_contact,
            q_email,
        ]

        quiz.save()

        print("Start quiz has been added.")

    def _add_new_poll_quiz(self):

        quiz = Quiz(name="NewPollQuiz", is_required=False)

        q_poll_name = Question(
            name="poll_name",
            message="Введи назву голосування",
            correct_answer_message="Прогрес - 1/4",
            wrong_answer_message="Неправильний ввід, спробуй ще раз",
        )

        q_question = Question(
            name="question",
            message="Введи саме питання, за що голосувати будемо?",
            correct_answer_message="Прогрес - 2/4",
            wrong_answer_message="Неправильний ввід, спробуй ще раз",
        )

        q_answer_options = Question(
            name="answer_options",
            message="Введи варіанти, які будуть присутні на голосуванні.\n\n<i>Наприклад:\nЗа\nПроти\n</i>\n\n<b>*Бланк ставиться автоматично!</b>",
            correct_answer_message="Прогрес - 3/4",
            wrong_answer_message="Неправильний ввід, спробуй ще раз",
        )

        q_poll_members = Question(
            name="poll_members",
            message="Введи нікнейми фулів які будуть присутні на голосуванні в стовпчик.\n\n<i>Наприклад:\n@Heav1kkk\n@vovaleha\n@cristina_sodzak</i>\n\n<b>*Себе також потрібно ввести!</b>",
            correct_answer_message="Голосування успішно додано!",
            wrong_answer_message="Неправильний ввід, спробуй ще раз",
        )

        quiz.questions = [q_poll_name, q_question, q_answer_options, q_poll_members]

        quiz.save()

        print("NewPollQuiz has been added.")
