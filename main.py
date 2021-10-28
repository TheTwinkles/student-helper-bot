import telebot
import rating_check
import logging

from telebot import types

import schedule
from auth_data import token


def update_keyboard(bot, message, logger):
    bot.send_message(message.chat.id, 'test', reply_markup=markup)
    logger.info('Command keyboard updated')


def create_keyboard(bot, message, logger):
    rating_btn = types.KeyboardButton('Рейтинг Гаряева')
    mil_schedule_btn = types.KeyboardButton('Расписание ВУЦ')
    markup.add(rating_btn)
    markup.add(mil_schedule_btn)
    bot.send_message(message.chat.id, "Выберите команду: ", reply_markup=markup)
    logger.info('Command keyboard created')


def telegram_bot(token, logger):
    bot = telebot.TeleBot(token)

    logger.info('Bot started')

    @bot.message_handler(commands=["start"])
    def start_message(message):
        bot.send_message(message.chat.id, "Привет")
        logger.info('Bot sent start message')
        create_keyboard(bot, message, logger)

    @bot.message_handler(commands=["check_rating"])
    def check_rating(message):
        try:
            logger.info('Bot received check rating updates command')
            rating_check.check_rating_updates(bot, message)
            # update_keyboard(bot, message, logger)
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
            military_schedule(message)
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
                rating_check.check_rating_updates(bot, message)
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
                schedule.military_schedule(bot, message, logger)
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
    logger = logging.getLogger('Bot')
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler("bot.log")  # file handler для логов

    # формат записи логов
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    # добавляем file handler к объекту логов
    logger.addHandler(fh)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    # запуск бота
    telegram_bot(token, logger)
