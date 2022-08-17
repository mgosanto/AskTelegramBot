from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from translate import Translator
import logging as log
import speech_recognition as sr
import os

def start(update, context):
    log.info(f' User "{update.message.from_user.id}" used command /start')
    msg = f'Hello, {update.message.from_user.first_name}.\n\n' \
          f'Default translation autodetects written language and translates it to english, you can change it for a more precise translation by using the command /fromlanguage and /tolanguage respectively.\n\n' \
          f'To receive the complete command list write /help.'
    context.bot.send_message(update.message.chat_id, msg)


def _help(update, context):
    log.info(f' User "{update.message.from_user.id}" used command /help')
    msg = 'BASIC COMMANDS\n\n' \
          '/start - Receive the welcome message\n' \
          '/help - Returns list of every AskTelegramBot command\n' \
          '/echo {sentence} - Returns the given sentence\n\n' \
          'TRANSLATION COMMANDS\n\n' \
          '/translate {sentence} - Translates the given sentence\n\n' \
          '/fromlanguage {language} - Updates the language which /translate will read. Language must be given in IETF language tag format or "autodetect" (accuracy decreases)\n\n' \
          '/tolanguage {language} - Updates the language /translate will return. Language must be given in IETF language tag format\n\n' \
          '/fastmode - Activates/Deactivates fast mode, which allows the bot to translate every message you send without using /translate.'
    context.bot.send_message(update.message.chat_id, msg)


def echo(update, context):
    log.info(f' User "{update.message.from_user.id}" used command /echo sending "{" ".join(context.args)}"')
    context.bot.send_message(update.message.chat_id, ' '.join(context.args))


def create_translator(context):
    if not context.user_data.get('from'):
        context.user_data['from'] = 'autodetect'
    if not context.user_data.get('to'):
        context.user_data['to'] = 'en'
    return Translator(from_lang=context.user_data.get('from'), to_lang=context.user_data.get('to'))


def translate(update, context):
    translator = create_translator(context)
    log.info(f' User "{update.message.from_user.id}" used command /translate sending "{" ".join(context.args)}"'
             f' from "{context.user_data.get("from")}" to "{context.user_data.get("to")}"')
    context.bot.send_message(update.message.chat_id, translator.translate(' '.join(context.args)))


def fromlanguage(update, context):
    log.info(f' User "{update.message.from_user.id}" used command /fromlanguage sending "{context.args[0]}"')
    context.user_data['from'] = context.args[0]
    context.bot.send_message(update.message.chat_id, 'Language updated.')


def tolanguage(update, context):
    log.info(f' User "{update.message.from_user.id}" used command /tolanguage sending "{context.args[0]}"')
    context.user_data['to'] = context.args[0]
    context.bot.send_message(update.message.chat_id, 'Language updated.')


def fastmode(update, context):
    log.info(f' User "{update.message.from_user.id}" used command /fastmode')
    if context.user_data.get('fastmode') is None:
        context.user_data['fastmode'] = False
    fast_mode = context.user_data.get('fastmode')
    context.user_data['fastmode'] = not fast_mode
    context.bot.send_message(update.message.chat_id, 'Fast mode deactivated.' if fast_mode else 'Fast mode activated.')


def fast_translate(update, context):
    if context.user_data.get('fastmode'):
        translator = create_translator(context)
        log.info(f' User "{update.message.from_user.id}" on fast mode translating "{update.message.text}"'
                 f' from "{context.user_data.get("from")}" to "{context.user_data.get("to")}"')
        context.bot.send_message(update.message.chat_id, translator.translate(update.message.text))


def speech_translate(update, context):
    log.info(f' User "{update.message.from_user.id}" translating speech')
    file_name = f'voice_messages/{update.message.voice.file_id}.mp3'
    update.message.voice.get_file().download(file_name)
    r = sr.Recognizer()
    with sr.AudioFile(file_name) as source:
        audio = r.record(source)
    print(r.recognize_sphinx(audio))
    os.remove(file_name)


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
    dispatcher.add_handler(MessageHandler(Filters.voice, speech_translate))
    dispatcher.add_handler(MessageHandler(Filters.text, fast_translate))
    # Starts the bot
    updater.start_polling()
    log.info('Bot launched')
    # Bot nonstop hearing the channel
    updater.idle()


if __name__ == '__main__':
    log.basicConfig(level=log.INFO)
    launch_bot()
