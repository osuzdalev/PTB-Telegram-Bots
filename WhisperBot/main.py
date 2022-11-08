import logging
import os
import time

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import whisper
from easynmt import EasyNMT

from config import *

# Configuring logging
log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("Logs.log")
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Send audio file for transcription")


def check_type(update: Update) -> (str, bool, str):
    if update.effective_message.voice:
        return "voice", update.effective_message.voice.duration <= FILE_DURATION_LIMIT, "audio.ogg"
    elif update.effective_message.audio:
        return "audio", update.effective_message.audio.duration <= FILE_DURATION_LIMIT, "audio.m4a"
    elif update.effective_message.video:
        return "video", update.effective_message.video.duration <= FILE_DURATION_LIMIT, "audio.mp4"
    elif update.effective_message.video_note:
        return "video_note", update.effective_message.video_note.duration <= FILE_DURATION_LIMIT, "audio.mp4"
    else:
        return "document", update.effective_message.document.file_size <= FILE_SIZE_LIMIT, "audio.mp4"


def transcribe(file_path: str) -> (str, str):
    transcribe_model = whisper.load_model("base")
    audio = whisper.load_audio(file_path)
    audio = whisper.pad_or_trim(audio)
    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio).to(transcribe_model.device)

    # detect the spoken language
    _, probs = transcribe_model.detect_language(mel)
    detected_language = max(probs, key=probs.get)
    print(f"Detected language: {detected_language}")

    # decode the audio
    options = whisper.DecodingOptions(fp16=False)
    result = whisper.decode(transcribe_model, mel, options)

    # print the recognized text
    print(result.text)

    return result.text, detected_language


def translate(transcribe_result: str) -> str:
    translation_model = EasyNMT('opus-mt')
    translation_result = translation_model.translate(transcribe_result, target_lang='en')
    print(translation_result)

    return translation_result


async def transcribe_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Downloading ...")

    audio_type, duration, file_name = check_type(update)

    if not duration:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="File too long (MAX = {})!".format(FILE_DURATION_LIMIT))
        return

    dir_name = "./tmp"
    file_path = dir_name + '/' + file_name
    logger.info("Downloading file from {}...".format(update.message.from_user.username))
    audio_file = await update.message.effective_attachment.get_file()
    await audio_file.download(file_path)

    while not os.path.isfile(file_path):
        print("Waiting for {} to be written".format(file_path))
        time.sleep(1)

    logger.info("Transcribing file {}...".format(file_path))

    transcribe_result, detected_language = transcribe(file_path)

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"Detected language: {detected_language}")

    await context.bot.send_message(chat_id=update.effective_chat.id, text=transcribe_result)

    # translate text to english if necessary
    if not (detected_language == "en"):
        translation_result = translate(transcribe_result)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=translation_result)


async def wrong_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_message.chat_id, text="wrong type of file")


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.AUDIO | filters.VOICE | filters.Document.AUDIO, transcribe_callback))
    application.add_handler(MessageHandler(filters.VIDEO | filters.VIDEO_NOTE, transcribe_callback))
    application.add_handler(MessageHandler(~ (filters.AUDIO | filters.VOICE | filters.Document.AUDIO), wrong_file))

    application.run_polling()


if __name__ == "__main__":
    main()
