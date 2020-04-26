import logging

from telegram.ext import ConversationHandler
from bot.selectors import select_place


def greet_user(bot, update):
    text = "Привет, это бот Eat is random\nотправь мне название блюда и свое местоположение.\nВ ответ я отправлю случайное заведение которое тебе подходит."
    update.message.reply_markdown(text)
    logging.info('User: %s, Message: %s',
                 update.message.chat.username, text)


def place_handler(bot, update, user_data):
    text = "пожалуйста введите название блюда"
    update.message.reply_markdown(text)
    logging.info('User: %s, Message: %s',
                 update.message.chat.username, text)

    return "get_dish_name"


def get_dish_name(bot, update, user_data):
    user_data["dish_name"] = update.message.text

    # text = "пожалуйста отправьте локацию"
    text = select_place.all_together(update.message.text)
    update.message.reply_markdown(text)
    logging.info('User: %s, Message: %s',
                 update.message.chat.username, text)

    return ConversationHandler.END
    # return "get_geo_data"


def get_geo_data(bot, update, user_data):
    print(update.message.location)

    text = "спасибо!"
    update.message.reply_markdown(text)
    logging.info('User: %s, Message: %s',
                 update.message.chat.username, text)

    return ConversationHandler.END
