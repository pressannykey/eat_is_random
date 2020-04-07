import logging

from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from bot import settings

# typing
from telegram import Update, Message, ReplyKeyboardRemove

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log'
                    )


def greet_user(bot, update: Update):
    text = "Привет, это бот Eat is random\nотправь мне название блюда и свое местоположение.\nВ ответ я случайное заведение которое тебе подходит."
    message: Message = update.message
    message.reply_markdown(text)
    logging.info('User: %s, Message: %s',
                 update.message.chat.username, text)


def location(bot, update):
    print(update.message.location)
    k = ReplyKeyboardRemove()
    update.message.reply_text(text=')')


def main():
    mybot = Updater(settings.BOT_API_KEY, request_kwargs=settings.PROXY)

    logging.info('Бот запускается')

    dp = mybot.dispatcher

    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("help", greet_user))

    dp.add_handler(MessageHandler(Filters.location, location))
    mybot.start_polling()
    mybot.idle()


if __name__ == '__main__':
    main()
