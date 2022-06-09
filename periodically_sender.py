import datetime
import threading
import time
import requests
from bs4 import BeautifulSoup
import config

# pars Bash.im
URL_JOKE = "http://bomz.org/bash/?bash=random"
URL_FACTS = "https://randstuff.ru/fact/"
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'accept': '*/*'}


def get_soup(url):
    html = requests.get(url, headers=HEADERS, params=None)
    if html.status_code == 200:
        return BeautifulSoup(html.text, 'html.parser')
    else:
        return "Error with parser " + str(url)


def get_content_facts(soup):
    if isinstance(soup, str):
        print(soup)
        return str(soup)
    else:
        items = soup.find_all('table')
        return items[0].get_text("\n", strip=True)


def get_content_joke(soup):
    if isinstance(soup, str):
        print(soup)
        return str(soup)
    else:
        items = soup.find_all('td',
                              style='border-right: 1px dashed #D8D8D8;border-bottom: 1px dashed #F0F0F0;border-top: 1px dashed #F0F0F0;')
        return items[1].get_text("\n", strip=True)


def send_message_periodically(bot):
    while True:
        time.sleep(43200)
        fact = get_content_facts(get_soup(URL_FACTS))
        bot.send_message(config.CHAT_ID, fact)
        time.sleep(43200)
        bot.send_message(config.CHAT_ID, get_content_joke(get_soup(URL_JOKE)))
        print("Periodically message was sent at ", datetime.datetime.now())
        time.sleep(43200)


def start_thread(bot):
    x = threading.Thread(target=send_message_periodically(bot),
                         args=('',),
                         daemon=True)
    x.start()
