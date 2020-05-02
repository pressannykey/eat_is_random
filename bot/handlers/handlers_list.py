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
        RegexHandler(
            "^Найти заведение по блюду$", functions.place_handler, pass_user_data=True
        ),
    ],
    states={
        "get_dish_name": [
            MessageHandler(Filters.text, functions.get_dish_name, pass_user_data=True)
        ],
        "get_geo_data": [
            MessageHandler(
                Filters.location, functions.get_geo_data, pass_user_data=True
            )
        ],
        "next_place_or_final": [
            RegexHandler("^Посмотреть еще$", functions.next_place, pass_user_data=True),
            RegexHandler("^Подходит$", functions.final, pass_user_data=True),
        ],
    },
    fallbacks=[],
)

handlers_list = [
    CommandHandler("start", functions.greet_user),
    RegexHandler("help", functions.greet_user),
    CommandHandler("place", functions.place_handler),
    place_getter,
]
