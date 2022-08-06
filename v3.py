from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from translate import Translator


def start(update, context):
    msg = f'Hello, {update.message.from_user.first_name}.\n\n' \
          f'Default translation autodetects written language and translates it to english, you can change it for a more precise translation by using the command /fromlanguage and /tolanguage respectively.\n\n' \
          f'To receive the complete command list write /help.'
    context.bot.send_message(update.message.chat_id, msg)


def _help(update, context):
    msg = 'BASIC COMMANDS\n\n' \
          '/start - Receive the welcome message\n' \
          '/help - Returns list of every AskTelegramBot command\n' \
          '/echo {sentence} - Returns the given sentence\n\n' \
          'TRANSLATION COMMANDS\n\n' \
          '/translate {sentence} - Translates the given sentence\n\n' \
          '/fromlanguage {language} - Updates the language which /translate will read. Language must be given in IETF language tag format\n\n' \
          '/tolanguage {language} - Updates the language /translate will return. Language must be given in IETF language tag format\n\n' \
          '/fastmode - Activates/Deactivates fast mode, which allows the bot to translate every message you send without using /translate.'
    context.bot.send_message(update.message.chat_id, msg)


def echo(update, context):
    context.bot.send_message(update.message.chat_id, ' '.join(context.args))


def translate(update, context):
    if not context.user_data.get('from'):
        context.user_data['from'] = 'autodetect'
    if not context.user_data.get('to'):
        context.user_data['to'] = 'en'
    translator = Translator(from_lang=context.user_data.get('from'), to_lang=context.user_data.get('to'))
    if context.user_data.get('fastmode'):
        context.bot.send_message(update.message.chat_id, translator.translate(update.message.text))
    else:
        if context.args:
            context.bot.send_message(update.message.chat_id, translator.translate(' '.join(context.args)))


def fromlanguage(update, context):
    context.user_data['from'] = context.args[0]
    context.bot.send_message(update.message.chat_id, 'Language updated.')


def tolanguage(update, context):
    context.user_data['to'] = context.args[0]
    context.bot.send_message(update.message.chat_id, 'Language updated.')


def fastmode(update, context):
    if context.user_data.get('fastmode') is None:
        context.user_data['fastmode'] = False
    fast_mode = context.user_data.get('fastmode')
    context.user_data['fastmode'] = not fast_mode
    context.bot.send_message(update.message.chat_id, 'Fast mode deactivated.' if fast_mode else 'Fast mode activated.')


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
    dispatcher.add_handler(CommandHandler('fastmode', fastmode))
    dispatcher.add_handler(MessageHandler(Filters.text, translate))
    # Starts the bot
    updater.start_polling()
    # Bot nonstop hearing the channel
    updater.idle()


if __name__ == '__main__':
    launch_bot()
