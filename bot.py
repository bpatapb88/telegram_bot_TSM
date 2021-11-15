# !/usr/bin/python3
import os

import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup

import config

bot = telebot.TeleBot(config.token)
COMMAND = 'psql -U postgres -d postgres -c '
chat_id = 0


@bot.message_handler(content_types=["new_chat_members"])
def foo(message):
    global chat_id
    print("start new member")
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


@bot.callback_query_handler(func=lambda call: True)
def login_user(call: CallbackQuery):
    data_id = int(call.data.split("_")[0])
    if data_id == call.from_user.id:
        bot.restrict_chat_member(chat_id, data_id, 0, True, True, True, True, True, True, True, True)
        bot.delete_message(chat_id, call.message.id)
    else:
        bot.answer_callback_query(call.id, "Ты уже зареган", show_alert=True)


@bot.message_handler(content_types=["left_chat_member"])
def foo(message):
    bot.reply_to(message, "Прощай, и ничего не общещай, и ничего не говори...")


@bot.message_handler(commands=['show_stat'])
def statistic(message):
    user = message.from_user
    mention = "[" + user.first_name + "](tg://user?id=" + str(user.id) + ")"
    if not if_user_exist(user):
        msg = f"Считай ты ничего не достиг {mention}. Зарегайся! а то чё ты как..."
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
    else:
        events = show_Category(user.id, "Events")
        media = show_Category(user.id, "Media")
        social = show_Category(user.id, "Social")
        achivki = show_Category(user.id, "Achievements")
        msg = f"Статистика {mention}: \n\n" + str(events) + str(media) + str(social) + str(achivki)
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")


def show_Category(user_id, category):
    sql_command = '"SELECT values -> \'' + category + '\' as \\"' + category + '\\" FROM users_tsm WHERE telegram_id = ' + str(
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
        msg = f"Спасибо {mention} за регистрацию"

    sql_command = '"INSERT INTO users_tsm (telegram_id,user_name) VALUES (' + str(
        user_reg.id) + ',\'' + str(user_reg.first_name) + '\')"'
    read = os.popen(COMMAND + sql_command).read()
    print("registration - " + str(read))
    if read.split()[0] == "INSERT":
        sql_command = '"UPDATE users_tsm SET values = json_build_object (\'Events\',json_build_object(\'BoardGame\',0,' \
                      '\'HikingTrip\',0,\'Creative\',0,\'Others\',0),\'Social\',json_build_object(\'Attended\',0,\'Chat\',0' \
                      ',\'InvitedFriends\',0),\'Media\',json_build_object(\'Meme\',0,\'Content\',0),\'Hidden\',' \
                      'json_build_object(\'exit\',0,\'horny\',0),\'Achievements\',json_build_array()) WHERE telegram_id=' + str(user_reg.id) + '" '
        read = os.popen(COMMAND + sql_command).read()
        print(read)
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "Ошибка! обратитесь к разработчику")


@bot.message_handler(content_types=["text"])
def handle_regular_messages(message):
    user_is_registered = if_user_exist(message.from_user)
    user_from = message.from_user.id
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
    elif message.chat.id == config.CHAT_ID and user_is_registered:
        # increment messages
        sql_command = '"SELECT values -> \'Social\' -> \'Chat\' FROM users_tsm WHERE telegram_id=' + str(
            message.from_user.id) + '"'
        read = os.popen(COMMAND + sql_command).read()
        current_value = int(read.split()[2])
        current_value += 1
        sql_command = '"UPDATE users_tsm SET values = jsonb_set(values::jsonb,\'{"Social","Chat"}\',' + str(
            current_value) + '::text::jsonb, false) WHERE telegram_id=' + str(message.from_user.id) + '" '
        read = os.popen(COMMAND + sql_command).read()
        print(str(read))

        achv = ""
        if current_value == 500:
            achv = "What does the fox say?"
        elif current_value == 1000:
            achv = "Small talk"
        elif current_value == 2500:
            achv = "Jibber Jabber"
        elif current_value == 5000:
            achv = "Oh, shut up"

        if achv != "":
            mention = "[" + message.from_user.first_name + "](tg://user?id=" + str(message.from_user.id) + ")"
            msg = f"Поздравляем! {mention} получил(a) ачивку - \"" + achv + "\""
            bot.send_message(config.CHAT_ID, msg, parse_mode="Markdown")
            add_achivment(achv, message.from_user.id)


def admin_answer(message, nominated_id, first_name):
    print("admin_answer - " + str(nominated_id))
    rmk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if message.text == "Events":
        rmk.add(KeyboardButton("BoardGame"), KeyboardButton("HikingTrip"), KeyboardButton("Creative"),
                KeyboardButton("Others"))
        msg = bot.send_message(message.chat.id, "Теперь выбери тип мероприятия", reply_markup=rmk)
        bot.register_next_step_handler(msg, lambda m: event_plus(m, nominated_id, first_name))
    elif message.text == "Social":
        rmk.add(KeyboardButton("Attended"), KeyboardButton("InvitedFriends"))
        msg = bot.send_message(message.chat.id, "Теперь выбери тип социализации", reply_markup=rmk)
        bot.register_next_step_handler(msg, lambda m: social_plus(m, nominated_id, first_name))
    elif message.text == "Media":
        rmk.add(KeyboardButton("Meme"), KeyboardButton("Content"))
        msg = bot.send_message(message.chat.id, "Теперь выбери тип медиа", reply_markup=rmk)
        bot.register_next_step_handler(msg, lambda m: media_plus(m, nominated_id, first_name))
    elif message.text == "Hidden":
        pass
    else:
        bot.send_message(message.chat.id, "Выбери из предложанных категорий")


def add_achivment(achiev, telegram_id):
    sql_command = '"UPDATE public.users_tsm SET values=jsonb_insert(values::jsonb, \'{Achievements, 1}\', \'\\"' + str(
        achiev) + '\\"\') ' \
                  'WHERE telegram_id=' + str(telegram_id) + ' and ' \
                                                            'NOT values::jsonb -> \'Achievements\' ? \'' + str(
        achiev) + '\'"'
    read = os.popen(COMMAND + sql_command).read()
    print("achivment was added \n" + str(read))


def media_plus(message, nominated_id, first_name):
    media_text = message.text
    mention = "[" + str(first_name) + "](tg://user?id=" + str(nominated_id) + ")"
    if media_text in {"Meme", "Content"}:
        sql_command = '"SELECT values -> \'Media\' -> \'' + media_text + '\' FROM users_tsm WHERE telegram_id=' + str(
            nominated_id) + '"'
        read = os.popen(COMMAND + sql_command).read()
        print(read)
        current_value = int(read.split()[2]) + 1
        sql_command = '"UPDATE users_tsm SET values = jsonb_set(values::jsonb,\'{"Media","' + media_text + '"}\',' + str(
            current_value) + '::text::jsonb, false) WHERE telegram_id=' + str(
            nominated_id) + '" '
        read = os.popen(COMMAND + sql_command).read()
        if read.split()[0] == "UPDATE" and read.split()[1] == '1':
            bot.send_message(message.chat.id, media_text + " successfully incremented! ")

        achive = ""
        if media_text == "Meme":
            if current_value == 1:
                achive = "Дратути"
            elif current_value == 5:
                achive = "Sad Pepe"
            elif current_value == 10:
                achive = "Welcome to my swamp"
            elif current_value == 20:
                achive = "Swole Doge"
        else:
            if current_value == 1:
                achive = "Camera man"
            elif current_value == 5:
                achive = "Content maker"
            elif current_value == 10:
                achive = "Peter Parker"
            elif current_value == 20:
                achive = "Я снимаю нахуй"

        if achive != "":
            msg = f"Поздравляем! {mention} получил(a) ачивку - \"" + achive + "\""
            bot.send_message(config.CHAT_ID, msg, parse_mode="Markdown")
            add_achivment(achive, nominated_id)

    else:
        bot.send_message(message.chat.id, "Выбери из предложанных медиа")


def social_plus(message, nominated_id, first_name):
    social_text = message.text
    mention = "[" + str(first_name) + "](tg://user?id=" + str(nominated_id) + ")"
    if social_text in {"Attended", "InvitedFriends"}:
        sql_command = '"SELECT values -> \'Social\' -> \'' + social_text + '\' FROM users_tsm WHERE telegram_id=' + str(
            nominated_id) + '"'
        read = os.popen(COMMAND + sql_command).read()
        print(read)
        current_value = int(read.split()[2]) + 1
        sql_command = '"UPDATE users_tsm SET values = jsonb_set(values::jsonb,\'{"Social","' + social_text + '"}\',' + str(
            current_value) + '::text::jsonb, false) WHERE telegram_id=' + str(
            nominated_id) + '" '
        read = os.popen(COMMAND + sql_command).read()
        if read.split()[0] == "UPDATE" and read.split()[1] == '1':
            bot.send_message(message.chat.id, social_text + " successfully incremented! ")
        achive = ""
        if social_text == "Attended":
            if current_value == 5:
                achive = "You look familiar"
            elif current_value == 10:
                achive = "One of us"
            elif current_value == 25:
                achive = "Seasoned veteran"
            elif current_value == 50:
                achive = "I have seen things you people wouldnt believe"
        else:
            if current_value == 1:
                achive = "We need each otter"

        if achive != "":
            msg = f"Поздравляем! {mention} получил(a) ачивку - \"" + achive + "\""
            bot.send_message(config.CHAT_ID, msg, parse_mode="Markdown")
            add_achivment(achive, nominated_id)

    else:
        bot.send_message(message.chat.id, "Выбери из предложанных социализаций")


def event_plus(message, nominated_id, first_name):
    event = message.text
    mention = "[" + str(first_name) + "](tg://user?id=" + str(nominated_id) + ")"
    if event in {"BoardGame", "HikingTrip", "Creative", "Others"}:
        sql_command = '"SELECT values -> \'Events\' -> \'' + event + '\' FROM users_tsm WHERE telegram_id=' + str(
            nominated_id) + '"'
        read = os.popen(COMMAND + sql_command).read()
        current_value = int(read.split()[2]) + 1
        sql_command = '"UPDATE users_tsm SET values = jsonb_set(values::jsonb,\'{"Events","' + event + '"}\',' + str(
            current_value) + '::text::jsonb, false) WHERE telegram_id=' + str(
            nominated_id) + '" '
        read = os.popen(COMMAND + sql_command).read()
        if read.split()[0] == "UPDATE" and read.split()[1] == '1':
            bot.send_message(message.chat.id, event + " successfully incremented! ")

        if current_value == 1:
            if event == "BoardGame":
                achiv = "I have some game"
            elif event == "HikingTrip":
                achiv = "I hope we dont get lost"
            elif event == "Creative":
                achiv = "Amateur"
            else:
                achiv = "Jack of all trades"
        elif current_value == 5:
            if event == "BoardGame":
                achiv = "Board game geek"
            elif event == "HikingTrip":
                achiv = "Basic Pathfinding"
            elif event == "Creative":
                achiv = "Edward Scissors Hands"
            else:
                achiv = "Outgoing"
        elif current_value == 10:
            if event == "BoardGame":
                achiv = "You do not dig straight down"
            elif event == "HikingTrip":
                achiv = "Elven Ranger"
            elif event == "Creative":
                achiv = "Creative class"
            else:
                achiv = "The home is where the heart is"
        elif current_value == 20:
            if event == "BoardGame":
                achiv = "Dungeon master"
            elif event == "HikingTrip":
                achiv = "One with Nature"
            elif event == "Creative":
                achiv = "Pen, Brush & Voice"
            else:
                achiv = ""
        else:
            achiv = ""

        if achiv != "":
            msg = f"Поздравляем! {mention} получил(a) ачивку - \"" + str(achiv) + "\""
            bot.send_message(config.CHAT_ID, msg, parse_mode="Markdown")
            add_achivment(str(achiv), nominated_id)

    else:
        bot.send_message(message.chat.id, "Выбери из предложанных мероприятий")


def if_user_exist(user):
    sql_command = '"SELECT "telegram_id" FROM users_tsm"'
    read = os.popen(COMMAND + sql_command).read()
    if str(user.id) in read:
        return True
    else:
        return False


if __name__ == '__main__':
    bot.infinity_polling()
