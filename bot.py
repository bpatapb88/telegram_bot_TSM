# !/usr/bin/python3
import datetime
import os
import threading
import time

import requests
from bs4 import BeautifulSoup

import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup

import config
import achivments_handler

bot = telebot.TeleBot(config.token)
COMMAND = 'psql -d raspdb -c '
chat_id = 0
OK = 1

# pars Bash.im
URL = "http://bomz.org/bash/?bash=random"
URL2 = "https://randstuff.ru/fact/"
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'accept': '*/*'}


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('td',
                          style='border-right: 1px dashed #D8D8D8;border-bottom: 1px dashed #F0F0F0;border-top: 1px dashed #F0F0F0;')
    return items[1].get_text("\n", strip=True)


def parse():
    html = get_html(URL)
    if html.status_code == 200:
        return get_content(html.text)
    else:
        return "Error with parser"


def get_content_fact(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('table')
    return items[0].get_text("\n", strip=True)


def parseFact():
    html = get_html(URL2)
    if html.status_code == 200:
        return get_content_fact(html.text)
    else:
        return "Error with parser facts"


def send_message_periodically(message):
    while True:
        bot.send_message(config.CHAT_ID, parseFact())
        time.sleep(43200)
        bot.send_message(config.CHAT_ID, parse())
        print("Periodically message was sent at ", datetime.datetime.now())
        time.sleep(43200)


@bot.message_handler(content_types=["new_chat_members"])
def foo(message):
    global chat_id
    print("start new member")
    print(str(message))
    new_user = message.new_chat_members[0]
    if not new_user.is_bot:
        mention = "[" + new_user.first_name + "](tg://user?id=" + str(new_user.id) + ")"
        welcome = f"Привет {mention} Жми на кнопку Зайти"
        chat_id = message.chat.id
        user_id = new_user.id
        bot.restrict_chat_member(message.chat.id, user_id, 0, False, False, False, False, False, False, False, False)
        inline_kb_button = InlineKeyboardButton("Зайти", callback_data=f"{user_id}_login")
        inline_kb = InlineKeyboardMarkup([[inline_kb_button]])
        bot.send_message(message.chat.id, welcome, reply_markup=inline_kb, parse_mode="Markdown")
        # invite Friend
        if if_user_exist(message.from_user):
            sql_command = '"SELECT values -> \'Social\' -> \'InvitedFriends\' FROM users_tsm WHERE telegram_id=' \
                          + str(message.from_user.id) + '"'
            read = os.popen(COMMAND + sql_command).read()
            print(read)
            current_value = int(read.split()[2]) + 1

            sql_command = '"UPDATE users_tsm SET values = jsonb_set(values::jsonb,\'{"Social","InvitedFriends"}\',' \
                          + str(current_value) + '::text::jsonb, false) WHERE telegram_id=' + str(
                message.from_user.id) + '" '
            read = os.popen(COMMAND + sql_command).read()
            print("InvitedFriends incremented " + str(read))


@bot.callback_query_handler(func=lambda call: True)
def login_user(call: CallbackQuery):
    data_id = int(call.data.split("_")[0])
    if data_id == call.from_user.id:
        bot.restrict_chat_member(chat_id, data_id, 0, True, True, True, True, True, True, True, True)
        if not if_user_exist(call.from_user):
            registration(call.from_user)
        bot.delete_message(chat_id, call.message.id)
    else:
        print("call.from - " + str(call.from_user.id) + "\n data_id-" + str(data_id))
        bot.answer_callback_query(call.id, "Ты уже зареган", show_alert=True)


@bot.message_handler(content_types=["left_chat_member"])
def foo(message):
    bot.reply_to(message, "Прощай, и ничего не общещай, и ничего не говори...")


@bot.message_handler(commands=['karma'])
def show_karma(message):
    sql_command = '"SELECT karma as \\"Karma\\",user_name as \\"First Name\\",nick_name as \\"User Name\\" ' \
                  'FROM users_tsm WHERE karma > 0 ORDER BY karma DESC"'
    read = os.popen(COMMAND + sql_command).read()
    bot.send_message(message.chat.id, str(read))


@bot.message_handler(commands=['show_stat'])
def statistic(message):
    user = message.from_user
    mention = "[" + user.first_name + "](tg://user?id=" + str(user.id) + ")"
    if not if_user_exist(user):
        msg = f"Считай ты ничего не достиг {mention}. Зарегайся! а то чё ты как..."
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
    else:
        events = show_category(user.id, "Events")
        media = show_category(user.id, "Media")
        social = show_category(user.id, "Social")
        achieves = show_category(user.id, "Achievements")
        msg = f"Статистика {mention}: \n\n" + str(events) + str(media) + str(social) + str(achieves)
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")


def show_category(user_id, category):
    sql_command = '"SELECT values -> \'' + category + '\' as \\"' + category + '\\" FROM users_tsm ' \
                                                                               'WHERE telegram_id = ' + str(
        user_id) + ' "'
    read = os.popen(COMMAND + sql_command).read()
    print(read)
    return read.strip().replace("(1 row)", "\n")


@bot.message_handler(commands=['reg_me'])
def answer(message):
    user_reg = message.from_user
    mention = "[" + user_reg.first_name + "](tg://user?id=" + str(user_reg.id) + ")"
    if if_user_exist(user_reg):
        msg = f"Юзер {mention} уже зарегистрирован!"
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
        return
    else:
        registration(user_reg)


def registration(user_reg):
    mention = "[" + user_reg.first_name + "](tg://user?id=" + str(user_reg.id) + ")"
    msg = f"Добро пожаловать, {mention}, в наш дружный и теплый чат\nВам тут очень рады. Мы организовываем разные активиты в Брне и не только.\n@transsiberianway - Инфоканал где все ближайшие мероприятия \nhttps://instagram.com/transsiberianway?utm_medium=copy_link - Инста \nПредставьтесь, пожалуйста и расскажите о себе! Нам интересно, вам полезно. А кто не представился - тот бот! \n"
    sql_command = '"INSERT INTO users_tsm (telegram_id,user_name, karma) VALUES (' + str(
        user_reg.id) + ',\'' + str(user_reg.first_name) + '\', 0)"'
    read = os.popen(COMMAND + sql_command).read()
    print("registration - " + str(read))
    if read.split()[2] == str(OK):
        sql_command = '"UPDATE users_tsm SET values = json_build_object (\'Events\',json_build_object(' \
                      '\'BoardGame\',0,\'HikingTrip\',0,\'Creative\',0,\'Others\',0),\'Social\',' \
                      'json_build_object(\'Attended\',0,\'Chat\',0,\'InvitedFriends\',0),\'Media\',' \
                      'json_build_object(\'Meme\',0,\'Content\',0),\'Hidden\',' \
                      'json_build_object(\'exit\',0,\'horny\',0),\'Achievements\',json_build_array()) ' \
                      'WHERE telegram_id=' + str(user_reg.id) + '" '
        read = os.popen(COMMAND + sql_command).read()
        print(read)
        if user_reg.username is not None:
            sql_command = '"UPDATE users_tsm SET nick_name = \'' + str(
                user_reg.username) + '\' WHERE telegram_id=' + str(user_reg.id) + '"'
            read = os.popen(COMMAND + sql_command).read()
        print("nick name set " + str(read))
        bot.send_message(config.CHAT_ID, msg, parse_mode="Markdown")
    else:
        bot.send_message(config.CHAT_ID, "Ошибка! обратитесь к разработчику")
        bot.send_message(config.CREATOR, str(user_reg))
        bot.send_message(config.CREATOR, str(read))


@bot.message_handler(content_types=["text"])
def handle_regular_messages(message):
    user_is_registered = if_user_exist(message.from_user)
    user_from = message.from_user.id

    # admin control action
    if message.chat.id == user_from and message.forward_from is not None:
        nominated_id = message.forward_from.id
        admins = bot.get_chat_administrators(config.CHAT_ID)
        is_admin = False
        for admin in admins:
            print("admin - " + str(admin))
            if admin.user.id == message.from_user.id:
                is_admin = True

        if not is_admin:
            return

        if not if_user_exist(message.forward_from):
            bot.send_message(user_from, "Пользователь не зарегестрирован")
            return

        mention = "[" + message.forward_from.first_name + "](tg://user?id=" + str(message.forward_from.id) + ")"
        rmk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        rmk.add(KeyboardButton("Events"), KeyboardButton("Social"), KeyboardButton("Media"), KeyboardButton("Hidden"))
        bot_msg = f"Что заслужил/а {mention} ?"
        msg = bot.send_message(user_from, bot_msg, parse_mode="Markdown", reply_markup=rmk)
        bot.register_next_step_handler(msg, lambda m: admin_answer(m, nominated_id, message.forward_from.first_name))

    # increment messages
    if message.chat.id == config.CHAT_ID and user_is_registered:
        if user_is_registered:
            sql_command = '"SELECT values -> \'Social\' -> \'Chat\' FROM users_tsm WHERE telegram_id=' + str(
                message.from_user.id) + '"'
            read = os.popen(COMMAND + sql_command).read()
            current_value = int(read.split()[2])
            current_value += 1
            sql_command = '"UPDATE users_tsm SET values = jsonb_set(values::jsonb,\'{"Social","Chat"}\',' + str(
                current_value) + '::text::jsonb, false) WHERE telegram_id=' + str(message.from_user.id) + '" '
            read = os.popen(COMMAND + sql_command).read()
            print("Chat incremented " + str(read))
            achivments_handler.achieve_chat(current_value, message)

    # karma
    if message.chat.id == config.CHAT_ID and message.reply_to_message is not None:
        lower_text = str(message.text).lower()
        nominated = message.reply_to_message.from_user
        mention = "[" + nominated.first_name + "](tg://user?id=" + str(nominated.id) + ")"
        if "хвалю" in lower_text and if_user_exist(nominated):
            if message.from_user.id == nominated.id:
                bot.send_message(message.chat.id,
                                 "Хвали себя перед зеркалом")
            else:
                sql_command = '"SELECT karma FROM users_tsm WHERE telegram_id = ' + str(nominated.id) + '"'
                read = os.popen(COMMAND + sql_command).read()
                current_karma = int(read.split()[2])
                sql_command = '"UPDATE users_tsm SET karma = karma + 1 WHERE telegram_id = ' + str(nominated.id) + '"'
                read = os.popen(COMMAND + sql_command).read()
                print("karma incremented \n" + str(read))
                bot.send_message(message.chat.id, f"Карму {mention} повысили до " + str(current_karma + 1),
                                 parse_mode="Markdown")
        elif "осуждаю" in lower_text and if_user_exist(nominated):
            if message.from_user.id == nominated.id:
                bot.send_message(message.chat.id,
                                 "Самокретично")
            else:
                sql_command = '"SELECT karma FROM users_tsm WHERE telegram_id = ' + str(nominated.id) + '"'
                read = os.popen(COMMAND + sql_command).read()
                current_karma = int(read.split()[2])
                print("bad " + str(current_karma))
                if current_karma > 0:
                    sql_command = '"UPDATE users_tsm SET karma = karma - 1 WHERE telegram_id = ' + str(
                        nominated.id) + '"'
                    read = os.popen(COMMAND + sql_command).read()
                    bot.send_message(message.chat.id, f"Карму {mention} понизили до " + str(current_karma - 1),
                                     parse_mode="Markdown")
                    print("karma decremented \n" + str(read))
                else:
                    bot.send_message(message.chat.id, f"Карма {mention} уже на нуле", parse_mode="Markdown")
        elif "осуждаю" in lower_text or "хвалю" in lower_text and not if_user_exist(nominated):
            print(str(nominated.is_bot))
            if not nominated.is_bot:
                bot.send_message(message.chat.id, f"Пользователь {mention} не зарегался", parse_mode="Markdown")


def admin_answer(message, nominated_id, first_name):
    print("admin_answer - " + str(nominated_id))
    rmk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if message.text == "Events":
        rmk.add(KeyboardButton("BoardGame"), KeyboardButton("HikingTrip"), KeyboardButton("Creative"),
                KeyboardButton("Others"))
        msg = bot.send_message(message.chat.id, "Теперь выбери тип мероприятия", reply_markup=rmk)
        bot.register_next_step_handler(msg, lambda m: achivments_handler.event_plus(m, nominated_id, first_name))
    elif message.text == "Social":
        rmk.add(KeyboardButton("Attended"), KeyboardButton("InvitedFriends"))
        msg = bot.send_message(message.chat.id, "Теперь выбери тип социализации", reply_markup=rmk)
        bot.register_next_step_handler(msg, lambda m: achivments_handler.social_plus(m, nominated_id, first_name))
    elif message.text == "Media":
        rmk.add(KeyboardButton("Meme"), KeyboardButton("Content"))
        msg = bot.send_message(message.chat.id, "Теперь выбери тип медиа", reply_markup=rmk)
        bot.register_next_step_handler(msg, lambda m: achivments_handler.media_plus(m, nominated_id, first_name))
    elif message.text == "Hidden":
        pass
    else:
        bot.send_message(message.chat.id, "Выбери из предложанных категорий")


def if_user_exist(user):
    sql_command = '"SELECT "telegram_id" FROM users_tsm"'
    read = os.popen(COMMAND + sql_command).read()
    if str(user.id) in read:
        return True
    else:
        return False


if __name__ == '__main__':
    x = threading.Thread(target=send_message_periodically,
                         args=('',),
                         daemon=True)
    x.start()
    bot.infinity_polling()
