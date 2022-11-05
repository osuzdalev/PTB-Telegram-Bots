import logging
import os
import time

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import whisper

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


async def transcribe_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Downloading voice message...")
    duration = update.effective_message.voice.duration
    file_type = update.effective_message.voice.mime_type

    dir_name = "./tmp"
    file_name = "audio.ogg"
    file_path = dir_name + '/' + file_name
    logger.info("Downloading file from {}...".format(update.message.from_user.username))
    audio_file = await update.message.effective_attachment.get_file()
    await audio_file.download(file_path)

    while not os.path.isfile(file_path):
        print("Waiting for {} to be written".format(file_path))
        time.sleep(1)

    logger.info("Transcribing file {}...".format(file_path))
    model = whisper.load_model("tiny")
    result = model.transcribe(file_path)
    print(result["text"])

    await context.bot.send_message(chat_id=update.effective_chat.id, text=result["text"])


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.AUDIO | filters.VOICE, transcribe_callback))

    application.run_polling()


if __name__ == "__main__":
    main()
