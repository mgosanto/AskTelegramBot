from telegram.ext import Updater, CommandHandler
from translate import Translator


def start(update, context):
    msg = f'Hello, {update.message.from_user.first_name}.\n\n' \
          f'Your default translation is {update.message.from_user.language_code.upper()} to EN, you can change them by using the command /fromlanguage and /tolanguage respectively.\n\n' \
          f'To receive the complete command list write /help.'
    context.bot.send_message(update.message.chat_id, msg)


def _help(update, context):
    msg = 'BASIC COMMANDS\n\n' \
          '/start - Receive the welcome message\n' \
          '/help - Returns list of every AskTelegramBot command\n' \
          '/echo {sentence} - Returns the given sentence\n\n' \
          'TRANSLATE COMMANDS\n\n' \
          '/translate {sentence} - Translates the given sentence\n\n' \
          '/fromlanguage {language} - Updates the language which /translate will read. Language must be given in IETF language tag format\n\n' \
          '/tolanguage {language} - Updates the language /translate will return. Language must be given in IETF language tag format'
    context.bot.send_message(update.message.chat_id, msg)


def echo(update, context):
    context.bot.send_message(update.message.chat_id, ' '.join(context.args))


def translate(update, context):
    global from_
    if from_ == '':
        from_ = update.message.from_user.language_code
    translator = Translator(from_lang=from_, to_lang=to_)
    context.bot.send_message(update.message.chat_id, translator.translate(' '.join(context.args)))


def fromlanguage(update, context):
    global from_
    from_ = context.args[0]
    context.bot.send_message(update.message.chat_id, 'Successfully updated.')


def tolanguage(update, context):
    global to_
    to_ = context.args[0]
    context.bot.send_message(update.message.chat_id, 'Successfully updated.')


def launch_bot():
    token = "5488564209:AAFpF8k5RzvPQi45mwdN6tpdgVuXJ97SlC4"
    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', _help))
    dispatcher.add_handler(CommandHandler('echo', echo))
    dispatcher.add_handler(CommandHandler('translate', translate))
    dispatcher.add_handler(CommandHandler('fromlanguage', fromlanguage))
    dispatcher.add_handler(CommandHandler('tolanguage', tolanguage))
    # Starts the bot
    updater.start_polling()
    # Bot nonstop hearing the channel
    updater.idle()


if __name__ == '__main__':
    from_ = ''
    to_ = 'en'
    launch_bot()
