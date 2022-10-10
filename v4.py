from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from translate import Translator
import logging as log
import speech_recognition as sr
import os
from gtts import gTTS
from pydub import AudioSegment
import uvicorn
from fastapi import FastAPI

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
          '/fastmode - Activates/Deactivates fast mode, which allows the bot to translate every message you send without using /translate\n\n' \
          '/toaudio {sentence} - Translates any given sentence and returns it as an audio'

    context.bot.send_message(update.message.chat_id, msg)


def echo(update, context):
    log.info(f' User "{update.message.from_user.id}" used command /echo sending "{" ".join(context.args)}"')
    context.bot.send_message(update.message.chat_id, ' '.join(context.args))


def get_translator(context):
    if not context.user_data.get('from'):
        context.user_data['from'] = 'autodetect'
    if not context.user_data.get('to'):
        context.user_data['to'] = 'en'
    return Translator(from_lang=context.user_data.get('from'), to_lang=context.user_data.get('to'))


def translate(update, context):
    translator = get_translator(context)
    log.info(f' User "{update.message.from_user.id}" used command /translate sending "{" ".join(context.args)}"'
             f' from "{context.user_data.get("from")}" to "{context.user_data.get("to")}"')
    context.bot.send_message(update.message.chat_id, translator.translate(' '.join(context.args)))


def fromlanguage(update, context):
    log.info(f' User "{update.message.from_user.id}" used command /fromlanguage sending "{context.args}"')
    if not context.args:
        context.bot.send_message(update.message.chat_id, f'From language is set to "{context.user_data.get("from")}"')
        return
    context.user_data['from'] = context.args[0]
    context.bot.send_message(update.message.chat_id, 'Language updated.')


def tolanguage(update, context):
    log.info(f' User "{update.message.from_user.id}" used command /tolanguage sending "{context.args}"')
    if not context.args:
        context.bot.send_message(update.message.chat_id, f'To language is set to "{context.user_data.get("to")}"')
        return
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
        translator = get_translator(context)
        log.info(f' User "{update.message.from_user.id}" on fast mode translating "{update.message.text}"'
                 f' from "{context.user_data.get("from")}" to "{context.user_data.get("to")}"')
        context.bot.send_message(update.message.chat_id, translator.translate(update.message.text))


def speech_translate(update, context):
    file_name = f'voice_messages/{update.message.voice.file_id}'
    fromlanguage = context.user_data.get('from')
    log.info(f' User "{update.message.from_user.id}" translating speech on file "{file_name}" from language "{fromlanguage}"')

    translator = get_translator(context)
    if not fromlanguage or fromlanguage == 'autodetect':
        context.bot.send_message(update.message.chat_id, 'Select a specific language using /fromlanguage')
        return

    ogg = file_name + '.ogg'
    wav = file_name + '.wav'
    update.message.voice.get_file().download(ogg)
    sound = AudioSegment.from_ogg(ogg)
    sound.export(wav, format='wav')
    r = sr.Recognizer()
    with sr.AudioFile(wav) as source:
        audio = r.record(source)
    os.remove(ogg)
    os.remove(wav)

    recognized_text = r.recognize_google(audio, language=context.user_data.get('from'))
    context.bot.send_message(update.message.chat_id, 'You said: ' + recognized_text)
    
    translated_text = translator.translate(recognized_text)

    gtts = gTTS(text=translated_text, lang=context.user_data.get("to"), slow=False)
    gtts.save('voice_messages/translation.mp3')
    context.bot.send_audio(chat_id=update.message.chat_id, audio=open('voice_messages/translation.mp3', 'rb'))
    os.remove('voice_messages/translation.mp3')


def toaudio(update, context):
    log.info(f' User "{update.message.from_user.id}" used command /toaudio sending "{" ".join(context.args)}"'
             f' from "{context.user_data.get("from")}" to "{context.user_data.get("to")}"')

    translator = get_translator(context)
    gtts = gTTS(text=translator.translate(' '.join(context.args)), lang=context.user_data.get("to"), slow=False)
    gtts.save('voice_messages/translation.mp3')
    context.bot.send_audio(chat_id=update.message.chat_id, audio=open('voice_messages/translation.mp3', 'rb'))
    os.remove('voice_messages/translation.mp3')


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
    dispatcher.add_handler(CommandHandler('toaudio', toaudio))
    dispatcher.add_handler(MessageHandler(Filters.voice, speech_translate))
    dispatcher.add_handler(MessageHandler(Filters.text, fast_translate))
    # Starts the bot
    updater.start_polling()
    log.info('Bot launched')
    # Bot nonstop hearing the channel
    updater.idle()


app = FastAPI()


@app.get("/")
def index():
    log.basicConfig(level=log.INFO)
    launch_bot()


if __name__ == '__main__':
    uvicorn.run("v4:app", port=8000, reload=True)
