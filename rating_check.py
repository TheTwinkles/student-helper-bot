import requests
import filecmp

from urllib.parse import urlencode


def check_rating_updates():
    base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
    public_key = 'https://disk.yandex.ru/i/n1KicdZ1pObPIg'

    final_url = base_url + urlencode(dict(public_key=public_key))
    response = requests.get(final_url)
    download_url = response.json()['href']

    download_response = requests.get(download_url)

    with open('oppr_new.pdf', "wb") as f:
        f.write(download_response.content)

    if filecmp.cmp('oppr_new.pdf', 'oppr_old.pdf', shallow=True):
        print("Нет изменений")
    else:
        print("Есть изменения")
