import logging

from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from telegram import  InlineKeyboardMarkup, InlineKeyboardButton

from bot import settings

# typing
from telegram import Update, Message, ReplyKeyboardRemove

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log'
                    )


def greet_user(bot, update: Update):
    text = 'Приветствую!'
    message: Message = update.message
    message.reply_text(text=text)
    logging.info('User: %s, Message: %s',
                 update.message.chat.username, text)


def location(bot, update):
    print(update.message.location)
    k = ReplyKeyboardRemove()
    update.message.reply_text(text=')')


def main():
    mybot = Updater(settings.API_KEY, request_kwargs=settings.PROXY)

    logging.info('Бот запускается')

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(MessageHandler(Filters.location, location))
    mybot.start_polling()
    mybot.idle()


if __name__ == '__main__':
    main()
