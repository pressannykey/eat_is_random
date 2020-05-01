from telegram.ext import CommandHandler, ConversationHandler, MessageHandler
from telegram.ext import Filters
from . import functions

place_getter = ConversationHandler(
    entry_points=[
        CommandHandler("place", functions.place_handler, pass_user_data=True),
        MessageHandler(Filters.text, functions.get_dish_name, pass_user_data=True),
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
    },
    fallbacks=[],
)

handlers_list = [
    CommandHandler("start", functions.greet_user),
    CommandHandler("help", functions.greet_user),
    place_getter,
]
