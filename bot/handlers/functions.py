import logging
import random

from telegram.ext import ConversationHandler
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup
from bot.selectors import select_place


def get_keyboard():
    my_keyboard = ReplyKeyboardMarkup(
        [["Найти заведение по блюду"]], resize_keyboard=True
    )
    return my_keyboard


def greet_user(bot, update):
    text = "Привет, это бот Eat is random\nЯ умею находить заведения по блюду.\nЧтобы начать работу, нажми кнопку 'Найти заведение'"
    update.message.reply_text(text, reply_markup=get_keyboard())
    logging.info("User: %s, Message: %s", update.message.chat.username, text)


def place_handler(bot, update, user_data):
    text = "Введи название блюда"
    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    logging.info("User: %s, Message: %s", update.message.chat.username, text)

    return "get_dish_name"


def get_dish_name(bot, update, user_data):
    user_data["dish_name"] = update.message.text

    # text = "пожалуйста отправьте локацию"

    places, direct_match = select_place.get_place_by_dish(update.message.text)

    if not places:
        text = "Ничего не нашлось:(\nХотите начать новый поиск? Нажмите 'Найти заведение по блюду'"
        update.message.reply_text(text, reply_markup=get_keyboard())
        return ConversationHandler.END

    user_data["places"] = places

    text = """{case} заведение: 
{name} с рейтингом {rating}, по адресу: {adress}. Тел: {phone_number}
В меню: {dishes}"""
    user_data["text"] = text

    if direct_match:
        case = "Мы нашли"
    else:
        case = "Точного совпадения не нашлось.\nВозможно, вам подойдет"

    user_data["case"] = case
    place = random.choice(user_data["places"])
    dishes = ", ".join(place[-1])
    answer = text.format(
        case=user_data["case"],
        name=place[1],
        rating=place[2],
        adress=place[3],
        phone_number=place[4],
        dishes=dishes,
    )
    reply_keyboard = [["Подходит", "Посмотреть еще"]]

    user_data["places"].remove(place)
    update.message.reply_text(
        answer,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    logging.info("User: %s, Message: %s", update.message.chat.username, answer)
    bot.send_location(
        chat_id=update.message.chat_id, latitude=59.933938, longitude=30.339296
    )

    return "next_place_or_final"


def next_place(bot, update, user_data):
    place = random.choice(user_data["places"])
    dishes = ", ".join(place[-1])
    answer = user_data["text"].format(
        case=user_data["case"],
        name=place[1],
        rating=place[2],
        adress=place[3],
        phone_number=place[4],
        dishes=dishes,
    )
    reply_keyboard = [["Подходит", "Посмотреть еще"]]

    user_data["places"].remove(place)
    update.message.reply_text(
        answer,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    logging.info("User: %s, Message: %s", update.message.chat.username, answer)
    bot.send_location(
        chat_id=update.message.chat_id, latitude=59.933938, longitude=30.339296
    )
    return ConversationHandler.END


def final(bot, update, user_data):
    text = "Приятного аппетита!"
    update.message.reply_text(text, reply_markup=get_keyboard())
    return ConversationHandler.END


def get_geo_data(bot, update, user_data):
    print(update.message.location)

    text = "спасибо!"

    update.message.reply_text(text)
    logging.info("User: %s, Message: %s", update.message.chat.username, text)

    return ConversationHandler.END
