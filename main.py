import telebot
import rating_check
import logging

from telebot import types
from auth_data import token


def main():
    logger = logging.getLogger('Bot')
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler("bot.log")  # file handler для логов

    # формат записи логов
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    # добавляем file handler к объекту логов
    logger.addHandler(fh)

    # запуск бота
    telegram_bot(token, logger)


def telegram_bot(token, logger):
    bot = telebot.TeleBot(token)

    logger.info('Bot started')

    @bot.message_handler(commands=["start"])
    def start_message(message):
        bot.send_message(message.chat.id, "Привет")
        logger.info('Bot sent start message')

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        rating_btn = types.KeyboardButton('Рейтинг Гаряева')
        markup.add(rating_btn)
        bot.send_message(message.chat.id, "Выберите команду: ", reply_markup=markup)
        logger.info('Command keyboard created')

    @bot.message_handler(commands=["check_rating"])
    def check_rating(message):
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

    #bot.infinity_polling()
    bot.polling()

# TODO клавиатура
# TODO расписание
# TODO рейтинг по фамилии


if __name__ == '__main__':
    main()
