import telebot
import rating_check
from auth_data import token


def telegram_bot(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=["start"])
    def start_message(message):
        bot.send_message(message.chat.id, "Привет")

    @bot.message_handler(content_types=["text"])
    def send_text(message):
        if message.text.lower() == "рейтинг гаряева":
            try:
                rating_check.check_rating_updates(bot, message)
            except Exception as ex:
                print(ex)
                bot.send_message(
                    message.chat.id,
                    "Ошибка"
                )

    bot.polling()


if __name__ == '__main__':
    telegram_bot(token)
