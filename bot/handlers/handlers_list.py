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
        MessageHandler(
            Filters.regex("^Найти заведение$"),
            functions.dish_handler,
            pass_user_data=True,
        ),
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
            MessageHandler(
                Filters.regex("^Посмотреть еще"),
                functions.next_place,
                pass_user_data=True,
            ),
            MessageHandler(
                Filters.regex("^Подходит"), functions.final, pass_user_data=True,
            ),
            MessageHandler(
                Filters.regex("^Новый поиск"),
                functions.dish_handler,
                pass_user_data=True,
            ),
        ],
    },
    fallbacks=[
        MessageHandler(Filters.text, functions.out_of_state, pass_user_data=True)
    ],
)

handlers_list = [
    place_getter,
    CommandHandler("start", functions.greet_user),
    CommandHandler("help", functions.greet_user),
]
