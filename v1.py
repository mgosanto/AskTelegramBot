from telegram.ext import Updater, CommandHandler


def start(update, context):
    msg = f'Hello, {update.message.from_user.first_name}.\n' \
          f'\n' \
          f'To receive the commands list write /help.'
    context.bot.send_message(update.message.chat_id, msg)


def _help(update, context):
    msg = '/start - Receive the welcome message\n' \
          '/echo {message} - Returns the given message'
    context.bot.send_message(update.message.chat_id, msg)


def echo(update, context):
    context.bot.send_message(update.message.chat_id, ' '.join(context.args))


def launch_bot():
    token = "5488564209:AAFpF8k5RzvPQi45mwdN6tpdgVuXJ97SlC4"
    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', _help))
    dispatcher.add_handler(CommandHandler('echo', echo))
    # Starts the bot
    updater.start_polling()
    # Bot nonstop hearing the channel
    updater.idle()


if __name__ == '__main__':
    launch_bot()
