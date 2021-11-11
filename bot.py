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
        return
    else:
        events = show_Category(user.id,"Events")
        media = show_Category(user.id,"Media")
        social = show_Category(user.id,"Social")
        msg = f"Скоро всё будет {mention}, ты только жди"

    bot.send_message(message.chat.id, events, parse_mode="Markdown")
    bot.send_message(message.chat.id, media, parse_mode="Markdown")
    bot.send_message(message.chat.id, social, parse_mode="Markdown")


def show_Category(user_id,category):
    sql_command = '"SELECT values -> \'' + category + '\' as ' + category + ' FROM users_tsm WHERE telegram_id = ' + str(user_id) + ' "'
    read = os.popen(COMMAND + sql_command).read()
    print(read)
    return read


@bot.message_handler(commands=['reg_me'])
def answer(message):
    user_reg = message.from_user
    mention = "[" + user_reg.first_name + "](tg://user?id=" + str(user_reg.id) + ")"
    if (if_user_exist(user_reg)):
        msg = f"Юзер {mention} уже зарегистрирован!"
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
        return
    else:
        msg = f"Спасибо {mention} за регистрацию"

    sql_command = '"INSERT INTO users_tsm (telegram_id,user_name) VALUES (' + str(
        user_reg.id) + ',\'' + str(user_reg.first_name) + '\')"'
    read = os.popen(COMMAND + sql_command).read()
    print("registration - " + str(read))
    if (read.split()[0] == "INSERT"):
        sql_command = '"UPDATE users_tsm SET values = json_build_object (\'Events\',json_build_object(\'BoardGame\',0,' \
                      '\'HikingTrip\',0,\'Creative\',0,\'Others\',0),\'Social\',json_build_object(\'Attend\',0,\'Chat\',0' \
                      ',\'Others\',0),\'Media\',json_build_object(\'Meme\',0,\'Content\',0),\'Hidden\',json_build_object(\'exit\',0,\'horny\',0)) WHERE telegram_id=' + str(
            user_reg.id) + '" '
        read = os.popen(COMMAND + sql_command).read()
        print(read)
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "Ошибка! обратитесь к разработчику")


@bot.message_handler(content_types=["text"])
def handle_regular_messages(message):
    print(str(message))

    admins = bot.get_chat_administrators(config.CHAT_ID)
    is_admin = False
    for admin in admins:
        print("admin - " + str(admin))
        if(admin.user.id == message.from_user.id):
            is_admin = True

    if not is_admin:
        return

    user_from = message.from_user.id
    if(message.chat.id == user_from and message.forward_from != None):
        nominated_id = message.forward_from.id
        if not if_user_exist(message.forward_from):
            bot.send_message(user_from, "Пользователь не зарегестрирован")
            return

        mention = "[" + message.forward_from.first_name + "](tg://user?id=" + str(message.forward_from.id) + ")"
        rmk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        rmk.add(KeyboardButton("Events"),KeyboardButton("Social"), KeyboardButton("Media"), KeyboardButton("Hidden"))
        bot_msg = f"Что заслужил/а {mention} ?"
        msg = bot.send_message(user_from, bot_msg, parse_mode="Markdown", reply_markup=rmk)
        bot.register_next_step_handler(msg,lambda m: admin_answer(m, nominated_id))


def admin_answer(message, nominated_id):
    print("admin_answer - " + str(nominated_id))
    if message.text == "Events":
        rmk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        rmk.add(KeyboardButton("BoardGame"), KeyboardButton("HikingTrip"), KeyboardButton("Creative"),
                KeyboardButton("Others"))
        msg = bot.send_message(message.chat.id, "Теперь выбери тип мероприятия", reply_markup=rmk)
        bot.register_next_step_handler(msg,lambda m: event_plus(m, nominated_id))
    elif message.text == "Social":
        pass
    elif message.text == "Media":
        pass
    elif message.text == "Hidden":
        pass
    else:
        bot.send_message(message.chat.id, "Выбери из предложанных категорий")


def event_plus(message,nominated_id):
    event = message.text

    if event in {"BoardGame","HikingTrip","Creative","Others"}:
        sql_command = '"SELECT values -> \'Events\' -> \'' + event + '\' FROM users_tsm WHERE telegram_id='+str(nominated_id)+'"'
        read = os.popen(COMMAND + sql_command).read()
        current_value = int(read.split()[2]) + 5
        print("current value " + str(current_value))
        print("nominated_user " + str(nominated_id))
        sql_command = '"UPDATE users_tsm SET values = jsonb_set(values::jsonb,\'{"Events","' + event + '"}\',((values::jsonb #> \'{"Events","' + event + '"}\')::int +1)::text::jsonb, false) WHERE telegram_id=' + str(
            nominated_id) + '" '
        read = os.popen(COMMAND + sql_command).read()
        if(read.split()[0] == "UPDATE" and read.split()[1] == '1'):
            bot.send_message(message.chat.id, event + " successfully incremented! ")
        print("event_plus " + str(read))
    else:
        bot.send_message(message.chat.id, "Выбери из предложанных мероприятий")


def if_user_exist(user):
    sql_command = '"SELECT "telegram_id" FROM users_tsm"'
    read = os.popen(COMMAND + sql_command).read()
    print("if_user_exist - \n" + read)
    if str(user.id) in read:
        return True
    else:
        return False


if __name__ == '__main__':
    bot.infinity_polling()
