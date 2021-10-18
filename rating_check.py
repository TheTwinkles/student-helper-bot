import requests
import filecmp
import os
import PyPDF2
import shutil
import logging

from urllib.parse import urlencode

# module_logger = logging.getLogger('Bot.rating_check')


def parse_mod_date(filename, separator=None):
    """
    Функция для парсинга и форматирования даты модификации PDF файла
    :param separator: используемый сепаратор для разделения частей даты
    :param filename: имя PDF файла
    :return: форматированная дата модификации файла
    """
    with open(filename, "rb") as pdf:
        pdf_reader = PyPDF2.PdfFileReader(pdf)  # "скармливаем" PdfFileReader наш PDF файл
        mod_date = pdf_reader.documentInfo["/ModDate"]  # вытаскиваем из метаданных файла дату последнего изменения
        # урезаем лишнюю информацию из mod_date
        mod_date = mod_date[2:]
        mod_date = mod_date[:14]
        # date
        year = mod_date[:4]
        month = mod_date[4:6]
        date = mod_date[6:8]
        # time
        hour = mod_date[8:10]
        minutes = mod_date[10:12]
        seconds = mod_date[12:14]
        # если не предполагается использование сепаратора то сохраняем дату последнего изменения по стандартному шаблону
        if separator is None:
            parsed_mod_date = f"{date}/{month}/{year} {hour}:{minutes}:{seconds}"
        # если необходимо использовать конкретный сепаратор, то сохраняем дату последнего изменения
        # с разделением данных с данным сепаратором
        else:
            parsed_mod_date = f"{date}{separator}{month}{separator}{year}{separator}" \
                              f"{hour}{separator}{minutes}{separator}{seconds}"
    return parsed_mod_date


def check_rating_updates(bot, message):
    """
    Функция для проверки обновления в рейтинговой таблице Гаряева
    :param bot: объект бота от которого отправляется сообщение
    :param message: объект сообщения пользователя
    :return:
    """
    logger = logging.getLogger("Bot.rating_check.check_rating_updates")

    base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'  # URL для загрузки с Я.Диска
    public_key = 'https://disk.yandex.ru/i/n1KicdZ1pObPIg'  # ссылка на конкретный файл

    final_url = base_url + urlencode(dict(public_key=public_key))  # создаем ссылку на по которой отправим get-запрос
    response = requests.get(final_url)  # посылаем get-запрос
    download_url = response.json()['href']  # получаем загрузочную ссылку

    download_response = requests.get(download_url)  # записываем содержимое файла с диска

    # TODO подумать над созданием отдельной папки для работы модуля проверки обновления рейтинга
    # if not os.path.isdir('rating_data'):
    #     os.mkdir('rating_data')
    #     data_path = 'rating_data'

    with open('oppr_new.pdf', "wb") as downloaded_file:
        downloaded_file.write(download_response.content)  # сохраняем в файл содержимое файла с диска
        logger.info("Downloaded file from Yandex.Disk")

    if filecmp.cmp('oppr_new.pdf', 'oppr_old.pdf', shallow=True):  # сравниваем содержимое файлов - старого и нового
        # если изменений нет, то пишем сообщение пользователю с датой последнего изменения и ссылкой на файл
        bot.send_message(message.chat.id, f"Нет изменений с {parse_mod_date('oppr_old.pdf')} "
                                                 f"\nСсылка на файл {public_key}")
        logger.info("Bot sent no changes reply")
    else:
        # если изменения есть, то пишем сообщение пользователю с датой изменения старого файла и нового + ссылка на файл
        bot.send_message(message.chat.id, f"Есть изменения c {parse_mod_date('oppr_old.pdf')}, "
                                          f"изменения внесены {parse_mod_date('oppr_new.pdf')} "
                                          f"\nСсылка на файл {public_key}")
        logger.info("Bot sent changes reply")

        # создаем папку для архива старых файлов с рейтингов и перемещаем туда файл,
        # который после проверки считается устаревшим
        if os.path.isdir('rating_archive'):
            logger.info("oppr_old.pdf archieved in rating_archive")
            shutil.move('oppr_old.pdf', f'rating_archive/oppr_old_{parse_mod_date("oppr_old.pdf", "_")}.pdf')
            logger.info("New file renamed as old")
            os.rename('oppr_new.pdf', 'oppr_old.pdf')
        else:
            logger.warning("Missing rating_archive directory")
            os.mkdir('rating_archive')
            logger.info("rating_archive directory created")
            logger.info("oppr_old.pdf archieved in rating_archive")
            shutil.move('oppr_old.pdf', f'rating_archive/oppr_old_{parse_mod_date("oppr_old.pdf", "_")}')
            logger.info("New file renamed as old")
            os.rename('oppr_new.pdf', 'oppr_old.pdf')
