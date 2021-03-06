import logging
import random

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.error import TelegramError
from telegram.ext import ConversationHandler

from bot.handlers import handlers_list
from bot.selectors import select_place


def get_keyboard():
    my_keyboard = ReplyKeyboardMarkup([["Найти заведение"]], resize_keyboard=True)
    return my_keyboard


def greet_user(bot, update):
    text = "Привет, это бот Eat is random!\nЯ умею находить заведения по блюду.\nЧтобы начать работу, нажми кнопку 'Найти заведение'"
    update.message.reply_text(text, reply_markup=get_keyboard())
    logging.info("User: %s, Message: %s", update.message.chat.username, text)

    key = handlers_list.place_getter._get_key(update)
    handlers_list.place_getter.update_state(ConversationHandler.END, key)


def choose_place(user_data):
    text = """{case} заведение: 
{name} с рейтингом {rating}, по адресу: {adress}. Тел: {phone_number}
В меню: {dishes}"""

    place = random.choice(user_data["places"])

    dish_list = place[-1]
    if len(place[-1]) > 7:
        dish_list = dish_list[:7]
    dishes = ", ".join(dish_list)

    answer = text.format(
        case=user_data["case"],
        name=place[1],
        rating=place[2],
        adress=place[3],
        phone_number=place[4],
        dishes=dishes,
    )

    user_data["places"].remove(place)

    return answer, place


def place_output(bot, update, user_data, keyboard):
    answer, place = choose_place(user_data)
    if keyboard:
        update.message.reply_text(
            answer,
            reply_markup=ReplyKeyboardMarkup(
                keyboard, one_time_keyboard=True, resize_keyboard=True,
            ),
        )
    else:
        update.message.reply_text(answer, reply_markup=ReplyKeyboardRemove())

    logging.info("User: %s, User_input: %s, Answer: %s", update.message.chat.username, user_data["dish_name"], answer)

    lat, lng = place[-2], place[-3]
    bot.send_location(chat_id=update.message.chat_id, latitude=lat, longitude=lng)


def dish_handler(bot, update, user_data):
    text = "Введи название блюда"
    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    logging.info("User: %s, Message: %s", update.message.chat.username, text)

    return "place_handler"


def place_handler(bot, update, user_data):
    user_data["dish_name"] = update.message.text

    places, direct_match = select_place.get_place_by_dish(update.message.text)

    if not places:
        text = "Ничего не нашлось :(\n" + welcome_text
        update.message.reply_text(text, reply_markup=get_keyboard())

        logging.info("User: %s, User_input: %s, Answer: %s", update.message.chat.username, user_data["dish_name"], text)
        return ConversationHandler.END

    user_data["places"] = places

    if direct_match:
        case = "Мы нашли"
    else:
        case = "Точного совпадения не нашлось.\nВозможно, вам подойдет"
    user_data["case"] = case

    reply_keyboard = [["Подходит!", "Посмотреть еще..."], ["Новый поиск"]]
    place_output(bot, update, user_data, reply_keyboard)
    if len(user_data["places"]) > 1:
        return "next_place_or_final"

    text = "Больше мест нет не нашлось.\n" + welcome_text
    update.message.reply_text(text, reply_markup=get_keyboard())

    logging.info("User: %s, User_input: %s, Answer: %s", update.message.chat.username, user_data["dish_name"], text)
    return ConversationHandler.END


def next_place(bot, update, user_data):
    if len(user_data["places"]) > 1:
        reply_keyboard = [["Подходит!", "Посмотреть еще..."], ["Новый поиск"]]
        place_output(bot, update, user_data, reply_keyboard)
        return "next_place_or_final"

    reply_keyboard = []
    place_output(bot, update, user_data, reply_keyboard)
    text = "Больше мест нет не нашлось.\n" + welcome_text
    update.message.reply_text(text, reply_markup=get_keyboard())

    logging.info("User: %s, User_input: %s, Answer: %s", update.message.chat.username, user_data["dish_name"], text)
    return ConversationHandler.END


def final(bot, update, user_data):
    text = "Приятного аппетита!"
    update.message.reply_text(text, reply_markup=get_keyboard())
    return ConversationHandler.END


# TODO: функция нигде не вызывается, нужно добавить обработку геопозиции
def get_geo_data(bot, update, user_data):
    print(update.message.location)

    text = "Cпасибо!"

    update.message.reply_text(text)
    logging.info("User: %s, Message: %s", update.message.chat.username, text)

    return ConversationHandler.END


def error_callback(bot, update, error):
    logging.warning(
        "User: %s, Message: %s caused error %s",
        update.message.chat.username,
        update.message.text,
        error,
    )
    text = "Что-то пошло не так :(\n" + welcome_text
    update.message.reply_text(text, reply_markup=get_keyboard())
    key = handlers_list.place_getter._get_key(update)

    handlers_list.place_getter.update_state(ConversationHandler.END, key)


def out_of_state(bot, update, user_data):
    update.message.reply_text(
        "Я не знаю такой команды :(\nХочешь начать новый поиск? Нажми 'Новый поиск'"
    )


welcome_text = "Хочешь начать новый поиск? Нажми 'Найти заведение'"
