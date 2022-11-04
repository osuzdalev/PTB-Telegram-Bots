"""
Telegram Bot to print pdf and txt files.
Users must first authorize themselves by entering the password using the command "/auth <password>".
This implementation works only for UNIX and uses "lp -d <printer> <file>" to print files (see function "print_file").
"""

import os
import pathlib
import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, filters, CommandHandler, MessageHandler, ContextTypes

from config import *


# Configuring logging
log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("PrintingBot.log")
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)


# TODO 4 constants are required: TOKEN, PRINTER_NAME, PASSWORD, FILES_DIR. Define them in the "config.py" file.
# Set the printer name with "lpstat -p"

# Verify directory where files for printing should be saved
pathlib.Path(FILES_DIR).mkdir(parents=True, exist_ok=True)

FILE_SIZE_LIMIT = 20 * 1024 * 1024  # 20MB

authorized_chats = set()


def print_file(file_path: str) -> None:
    os.system('lp -d {} {}'.format(PRINTER_NAME, file_path))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("User {} started...".format(update.message.from_user.username))
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Welcome! Authorize by \"/auth <password>\" to print files.")


def auth_passed(update: Update) -> bool:
    return update.message.chat_id in authorized_chats


async def authorize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = ''.join(context.args)

    if auth_passed(update):
        logger.info("User {} already authorized multiple times.".format(update.message.from_user.username))
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You already authorized!")
        return

    if PASSWORD == args:
        authorized_chats.add(update.message.chat_id)
        logger.info("User {} authorized.".format(update.message.from_user.username))
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Now you can print files via sending.")
    else:
        logger.info("User {} entered wrong password: {}.".format(update.message.from_user.username, args))
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Wrong password!")


async def callback_print_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not auth_passed(update):
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Need to authorize with \"/auth <password>\".")
        return

    file_name = update.message.document.file_name
    file_size = update.message.document.file_size

    if file_size > FILE_SIZE_LIMIT:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="File is too big ({} > {})!".format(file_size, FILE_SIZE_LIMIT))
        return

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Downloading file...")

    file_path = FILES_DIR + '/' + file_name

    logger.info("Downloading file {} from {}...".format(file_name, update.message.from_user.username))
    new_file = await update.message.effective_attachment.get_file()
    await new_file.download('file_name')
    logger.info("Downloaded  file {} from {}!".format(file_name, update.message.from_user.username))

    logger.info("Printing file {}...".format(file_path))
    print_file(file_path)

    logger.info("File {} sent for printing on {}!".format(file_path, PRINTER_NAME))
    await context.bot.send_message(chat_id=update.effective_chat.id, text="File Printing")


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('auth', authorize))
    application.add_handler(MessageHandler(filters.Document.ALL, callback_print_file))

    logger.info("Listening...")
    application.run_polling()
