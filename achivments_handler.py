import os

from bot import bot
from bot import COMMAND
import config


def media_plus(message, nominated_id, first_name):
    media_text = message.text
    mention = "[" + str(first_name) + "](tg://user?id=" + str(nominated_id) + ")"
    if media_text in {"Meme", "Content"}:
        sql_command = '"SELECT values -> \'Media\' -> \'' + media_text + '\' FROM users_tsm WHERE telegram_id=' \
                      + str(nominated_id) + '"'
        read = os.popen(COMMAND + sql_command).read()
        print(read)
        current_value = int(read.split()[2]) + 1
        sql_command = '"UPDATE users_tsm SET values = jsonb_set(values::jsonb,\'{"Media","' + media_text + '"}\',' \
                      + str(current_value) + '::text::jsonb, false) WHERE telegram_id=' + str(nominated_id) + '" '
        read = os.popen(COMMAND + sql_command).read()
        if read.split()[0] == "UPDATE" and read.split()[1] == '1':
            bot.send_message(message.chat.id, media_text + " successfully incremented! ")

        achieve = ""
        if media_text == "Meme":
            if current_value == 1:
                achieve = "Дратути"
            elif current_value == 5:
                achieve = "Sad Pepe"
            elif current_value == 10:
                achieve = "Welcome to my swamp"
            elif current_value == 20:
                achieve = "Swole Doge"
        else:
            if current_value == 1:
                achieve = "Camera man"
            elif current_value == 5:
                achieve = "Content maker"
            elif current_value == 10:
                achieve = "Peter Parker"
            elif current_value == 20:
                achieve = "Я снимаю нахуй"

        if achieve != "":
            msg = f"Поздравляем! {mention} получил(a) ачивку - \"" + achieve + "\""
            bot.send_message(config.CHAT_ID, msg, parse_mode="Markdown")
            add_achievement(achieve, nominated_id)

    else:
        bot.send_message(message.chat.id, "Выбери из предложанных медиа")


def add_achievement(achieve, telegram_id):
    sql_command = '"UPDATE public.users_tsm SET values=jsonb_insert(values::jsonb, \'{Achievements, 1}\', \'\\"' + str(
        achieve) + '\\"\') ' \
                  'WHERE telegram_id=' + str(telegram_id) + ' and ' \
                                                            'NOT values::jsonb -> \'Achievements\' ? \'' + str(
        achieve) + '\'"'
    read = os.popen(COMMAND + sql_command).read()
    print("achievement was added \n" + str(read))


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
                achieve = "I have some game"
            elif event == "HikingTrip":
                achieve = "I hope we dont get lost"
            elif event == "Creative":
                achieve = "Amateur"
            else:
                achieve = "Jack of all trades"
        elif current_value == 5:
            if event == "BoardGame":
                achieve = "Board game geek"
            elif event == "HikingTrip":
                achieve = "Basic Pathfinding"
            elif event == "Creative":
                achieve = "Edward Scissors Hands"
            else:
                achieve = "Outgoing"
        elif current_value == 10:
            if event == "BoardGame":
                achieve = "You do not dig straight down"
            elif event == "HikingTrip":
                achieve = "Elven Ranger"
            elif event == "Creative":
                achieve = "Creative class"
            else:
                achieve = "The home is where the heart is"
        elif current_value == 20:
            if event == "BoardGame":
                achieve = "Dungeon master"
            elif event == "HikingTrip":
                achieve = "One with Nature"
            elif event == "Creative":
                achieve = "Pen, Brush & Voice"
            else:
                achieve = ""
        else:
            achieve = ""

        if achieve != "":
            msg = f"Поздравляем! {mention} получил(a) ачивку - \"" + str(achieve) + "\""
            bot.send_message(config.CHAT_ID, msg, parse_mode="Markdown")
            add_achievement(str(achieve), nominated_id)

    else:
        bot.send_message(message.chat.id, "Выбери из предложанных мероприятий")


def social_plus(message, nominated_id, first_name):
    social_text = message.text
    mention = "[" + str(first_name) + "](tg://user?id=" + str(nominated_id) + ")"
    if social_text in {"Attended", "InvitedFriends"}:
        sql_command = '"SELECT values -> \'Social\' -> \'' + social_text + '\' FROM users_tsm WHERE telegram_id=' \
                      + str(nominated_id) + '"'
        read = os.popen(COMMAND + sql_command).read()
        print(read)
        current_value = int(read.split()[2]) + 1
        sql_command = '"UPDATE users_tsm SET values = jsonb_set(values::jsonb,\'{"Social","' + social_text + '"}\',' \
                      + str(current_value) + '::text::jsonb, false) WHERE telegram_id=' + str(nominated_id) + '" '
        read = os.popen(COMMAND + sql_command).read()
        if read.split()[0] == "UPDATE" and read.split()[1] == '1':
            bot.send_message(message.chat.id, social_text + " successfully incremented! ")
        achieve = ""
        if social_text == "Attended":
            if current_value == 5:
                achieve = "You look familiar"
            elif current_value == 10:
                achieve = "One of us"
            elif current_value == 25:
                achieve = "Seasoned veteran"
            elif current_value == 50:
                achieve = "I have seen things you people wouldnt believe"
        else:
            if current_value == 1:
                achieve = "We need each otter"

        if achieve != "":
            msg = f"Поздравляем! {mention} получил(a) ачивку - \"" + achieve + "\""
            bot.send_message(config.CHAT_ID, msg, parse_mode="Markdown")
            add_achievement(achieve, nominated_id)

    else:
        bot.send_message(message.chat.id, "Выбери из предложанных социализаций")


def achieve_chat(current_value, message):
    archive = ""
    if current_value == 500:
        archive = "What does the fox say?"
    elif current_value == 1000:
        archive = "Small talk"
    elif current_value == 2500:
        archive = "Jibber Jabber"
    elif current_value == 5000:
        archive = "Oh, shut up"

    if archive != "":
        print("chat achievement was raised")
        mention = "[" + message.from_user.first_name + "](tg://user?id=" + str(message.from_user.id) + ")"
        msg = f"Поздравляем! {mention} получил(a) ачивку - \"" + archive + "\""
        bot.send_message(config.CHAT_ID, msg, parse_mode="Markdown")
        add_achievement(archive, message.from_user.id)

