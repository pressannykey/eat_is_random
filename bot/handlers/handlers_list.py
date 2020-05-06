from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    RegexHandler,
)
from telegram.ext import Filters
from . import functions

place_getter = ConversationHandler(
    entry_points=[
        RegexHandler("^Найти заведение$", functions.dish_handler, pass_user_data=True),
    ],
    states={
        "place_handler": [
            MessageHandler(Filters.text, functions.place_handler, pass_user_data=True)
        ],
        # TODO: стейт не используется, нужно добавить обработку геопозиции
        "get_geo_data": [
            MessageHandler(
                Filters.location, functions.get_geo_data, pass_user_data=True
            )
        ],
        "next_place_or_final": [
            RegexHandler("^Посмотреть еще", functions.next_place, pass_user_data=True),
            RegexHandler("^Подходит", functions.final, pass_user_data=True),
            RegexHandler("^Новый поиск", functions.dish_handler, pass_user_data=True),
        ],
    },
    fallbacks=[],
)

handlers_list = [
    CommandHandler("start", functions.greet_user),
    CommandHandler("help", functions.greet_user),
    place_getter,
]
