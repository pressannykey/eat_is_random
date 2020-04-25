from .handlers_list import handlers_list


def set_handlers(bot_dispatcher):
    for handler in handlers_list:
        bot_dispatcher.add_handler(handler)
