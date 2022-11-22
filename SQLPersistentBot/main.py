from configparser import ConfigParser
import logging
from uuid import uuid4

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from SqliteBasePersistence import SqliteBasePersistence

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

CONSTANTS = ConfigParser()
CONSTANTS.read("../constants.ini")


async def put(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Usage: /put value"""
    # Generate ID
    key = str(uuid4())
    value = ' '.join(_.args)

    # Store value
    await application.persistence.update_user_data(user_id=update.effective_user.id, data=[key, value])
    # Send the key to the user
    await update.message.reply_text(key)


async def fetch(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Usage: /fetch <uuid>"""
    text = await application.persistence.fetch_user_data(_.args[0])
    await update.message.reply_text(text)


async def remove(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    # Remove value from data
    await application.persistence.drop_user_data(update.effective_user.id)
    await update.message.reply_text("item removed")


async def get(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    text: str = await application.persistence.get_user_data()
    await update.message.reply_text(text)

if __name__ == '__main__':
    sqlite_base_persistence = SqliteBasePersistence()
    sqlite_base_persistence.connect_database(CONSTANTS.get("PTB_PLAYGROUND", "DATABASE_FILEPATH"))

    application = Application.builder()\
        .token(CONSTANTS.get("PTB_PLAYGROUND", "PTB_PLAYGROUND_TOKEN"))\
        .persistence(persistence=sqlite_base_persistence)\
        .build()

    application.add_handler(CommandHandler('put', put))
    application.add_handler(CommandHandler('fetch', fetch))
    application.add_handler(CommandHandler('remove', remove))
    application.add_handler(CommandHandler('get', get))

    application.run_polling()
