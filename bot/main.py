import logging
from telegram.ext import Updater
from bot import settings
from bot.handlers import set_handlers


def main():
    my_bot = Updater(settings.BOT_API_KEY, request_kwargs=settings.PROXY)
    logging.info('Бот запускается')

    dp = my_bot.dispatcher
    set_handlers(dp)

    my_bot.start_polling()
    my_bot.idle()


if __name__ == '__main__':
    main()
