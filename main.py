import telebot
import logging
import schedule
import threading
import time
import rating_check

from telebot import types
from multiprocessing import *

import university_schedule
from auth_data import token


def create_keyboard(bot, message, logger):
    """
    Функция для создания клавиатуры
    :param bot: Объект бота
    :param message: Объект сообщения из чата
    :param logger: Объект логгера для логирования
    :return: Возвращает готовую разметку клавиатуры
    """
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    rating_btn = types.KeyboardButton('Рейтинг Гаряева')
    mil_schedule_btn = types.KeyboardButton('Расписание ВУЦ')
    markup.add(rating_btn)
    markup.add(mil_schedule_btn)
    bot.send_message(message.chat.id, "Привет", reply_markup=markup)
    logger.info('Command keyboard created')
    return markup


def check_users(message):
    """
    Функция для проверки наличия чата в "базе данных чатов"
    :param message: Объект сообщения из чата
    :return: Возвращает False, если чат уже есть в БД, и возвращает True, если чата нет в БД
    """
    f = open('chats.txt', 'r')
    chats = f.readlines()
    for chat_id in chats:
        if message.chat.id == chat_id:
            return False
    f.close()
    return True


def telegram_bot(token, logger):
    bot = telebot.TeleBot(token)  # авторизация бота в телеграме
    logger.info('Bot started')

    def start_autocheck_process():  # запуск Process для автоматической проверки рейтинга Гаряева
        Process(target=ProcessSchedule.start_schedule, args=()).start()

    class ProcessSchedule:  # Class для работы с модулем schedule

        @staticmethod
        def start_schedule():  # запуск schedule
            # параметры для schedule
            schedule.every().hour.do(ProcessSchedule.rating_autocheck())

            while True:  # запуск цикла
                schedule.run_pending()
                time.sleep(1)

        # функции для выполнения заданий по времени
        @staticmethod
        def rating_autocheck():  #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            f = open('chats.txt', 'r')
            chats = f.readlines()
            for chat_id in chats:
                rating_check.check_rating_updates(bot, chat_id, auto_check=True)
            f.close()

    @bot.message_handler(commands=["start"])
    def start_message(message):
        bot.send_message(message.chat.id, "Выберите команду: ", reply_markup=create_keyboard(bot, message, logger))
        f = open('chats.txt', 'a')  # открываем файл для записи id чата с пользователем
        if check_users(message):  # проверяем есть ли чат в БД
            f.write(str(message.chat.id) + '\n')
        f.close()
        logger.info('Bot sent start message')

    @bot.message_handler(commands=["check_rating"])
    def check_rating(message):
        try:
            logger.info('Bot received check rating updates command')
            if not check_users(message):
                start_autocheck_process()
                rating_check.check_rating_updates(bot, message.chat.id)
            else:
                bot.send_message(message.chat.id, "Сначала используйте команду /start")
        except Exception as ex:
            logger.error(ex)
            print(ex)
            bot.send_message(
                message.chat.id,
                "Ошибка"
            )

    @bot.message_handler(commands=["military_schedule"])
    def military_schedule(message):
        try:
            logger.info('Bot received check military schedule command')
            university_schedule.military_schedule(message)
        except Exception as ex:
            logger.error(ex)
            print(ex)
            bot.send_message(
                message.chat.id,
                "Ошибка"
            )

    @bot.message_handler(content_types=["text"])
    def send_reply(message):
        logger.info('Bot received message')
        if message.text.lower() == "рейтинг гаряева":
            try:
                logger.info('Bot received check rating updates command')
                if not check_users(message):
                    rating_check.check_rating_updates(bot, message.chat.id)
                else:
                    bot.send_message(message.chat.id, "Сначала используйте команду /start")
            except Exception as ex:
                logger.error(ex)
                print(ex)
                bot.send_message(
                    message.chat.id,
                    "Ошибка"
                )
        if message.text.lower() == 'расписание вуц':
            try:
                logger.info('Bot received check military schedule command')
                university_schedule.military_schedule(bot, message, logger)
            except Exception as ex:
                logger.error(ex)
                print(ex)
                bot.send_message(
                    message.chat.id,
                    "Ошибка"
                )

    # bot.infinity_polling()
    bot.polling()


# TODO клавиатура -> V
# TODO рейтинг по фамилии
# TODO расписание
# TODO расписание для военки


if __name__ == '__main__':
    logger = logging.getLogger('Bot')  # создание логгера
    logger.setLevel(logging.INFO)  # настройка уровня логгинга

    fh = logging.FileHandler("bot.log")  # file handler для логов

    # формат записи логов
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    # добавляем file handler к объекту логов
    logger.addHandler(fh)

    # запуск бота
    telegram_bot(token, logger)
