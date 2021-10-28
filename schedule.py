import requests
import os
import screenshoter

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def military_schedule(bot, message, logger):

    url = 'https://mgsu.ru/education/Voennaya_kafedra/Voennaya_kaf_segodnya/' \
          'ПДФ%20Расписание%20Четверг%20Октябрь%202021%20А3.pdf'
    # TODO пофиксить баг со скачиванием
    # session = requests.Session()
    # retry = Retry(connect=3, backoff_factor=0.5)
    # adapter = HTTPAdapter(max_retries=retry)
    # session.mount('http://', adapter)
    # session.mount('https://', adapter)
    #
    # response = session.get(url)
    response = requests.get(url)  # посылаем get-запрос

    data_path = 'schedule_data/'
    if not os.path.isdir('schedule_data'):
        os.mkdir('schedule_data')

    with open(data_path + 'mil_schedule_new.pdf', "wb") as downloaded_file:
        downloaded_file.write(response.content)
        logger.info("Downloaded file with military schedule")

    screenshoter.make_scrsht('mil_schedule_new.pdf')
    bot.send_document(message.chat.id, open(r'mil_schedule_new.pdf', 'rb'))
