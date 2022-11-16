from configparser import ConfigParser
import logging
import sys

from telegram import ReplyKeyboardMarkup, Update, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    PicklePersistence,
    CallbackQueryHandler
)

CONSTANTS = ConfigParser()
CONSTANTS.read("../constants.ini")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

START_ROUTE, COMPUTER, PHONE = range(3)
COMPUTER_START_OVER, COMPUTER_SCREEN, COMPUTER_KEYBOARD, COMPUTER_PROCESSOR, COMPUTER_GRAPHIC_CARD = range(5)
PHONE_START_OVER, PHONE_SCREEN, PHONE_KEYBOARD, PHONE_PROCESSOR, PHONE_GRAPHIC_CARD = range(5)


async def start(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Stuff"""
    user = update.message.from_user
    logger.info("Bot started by user {}".format(user.username))

    await update.message.reply_text("Welcome!\nType /faq to find an easy fix or\n"
                                    "/request to post an order and be connected to a contractor.")


async def faq(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    """Stuff"""
    logger.info("faq()")

    keyboard = [
        [InlineKeyboardButton(text="Computer", callback_data=COMPUTER),
         InlineKeyboardButton(text="Phone", callback_data=PHONE)]
    ]
    inline_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Select a device", reply_markup=inline_markup)

    return START_ROUTE


async def start_over(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt same text & keyboard as `faq` does but not as new message"""
    logger.info("start_over()")
    # Get CallbackQuery from Update
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()
    keyboard = [
        [InlineKeyboardButton(text="Computer", callback_data=COMPUTER),
         InlineKeyboardButton(text="Phone", callback_data=PHONE)]
    ]
    inline_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Select a device", reply_markup=inline_markup)

    return START_ROUTE


async def computer(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    """Stuff"""
    logger.info("computer()")
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton(text="Computer Screen", callback_data=COMPUTER_SCREEN),
         InlineKeyboardButton(text="Computer Keyboard", callback_data=COMPUTER_KEYBOARD)],
        [InlineKeyboardButton(text="Computer Processor", callback_data=COMPUTER_PROCESSOR),
         InlineKeyboardButton(text="Computer Graphic Card", callback_data=COMPUTER_GRAPHIC_CARD)],
        [InlineKeyboardButton(text="<< BACK", callback_data=COMPUTER_START_OVER)]
    ]
    inline_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text="Select a component", reply_markup=inline_markup)

    return COMPUTER


async def computer_screen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons. This is the end point of the conversation."""
    logger.info("computer_screen()")
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(text="Here is the answer to your question:\n"
                                       "Lorem Ipsum is simply dummy text of the printing and typesetting industry. "
                                       "Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, "
                                       "when an unknown printer took a galley of type and scrambled it to make a"
                                       "type specimen book. It has survived not only five centuries, but also the leap "
                                       "into electronic typesetting, remaining essentially unchanged. "
                                       "It was popularised in the 1960s with the release of Letraset sheets containing "
                                       "Lorem Ipsum passages, and more recently with desktop publishing software "
                                       "like Aldus PageMaker including versions of Lorem Ipsum.")
    await context.bot.send_photo(query.message.chat_id,
                                 "https://i.pcmag.com/imagery/roundups/05ersXu1oMXozYJa66i9GEo-38..v1657319390.jpg")
    return ConversationHandler.END


async def phone(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    """Stuff"""
    logger.info("phone()")
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton(text="Phone Screen", callback_data=PHONE_SCREEN),
         InlineKeyboardButton(text="Phone Keyboard", callback_data=PHONE_KEYBOARD)],
        [InlineKeyboardButton(text="Phone Processor", callback_data=PHONE_PROCESSOR),
         InlineKeyboardButton(text="Phone Graphic Card", callback_data=PHONE_GRAPHIC_CARD)],
        [InlineKeyboardButton(text="<< BACK", callback_data=PHONE_START_OVER)]
    ]
    inline_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text="Select a component", reply_markup=inline_markup)

    return PHONE


async def phone_screen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons. This is the end point of the conversation."""
    logger.info("phone_screen()")
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(text="Here is the answer to your question:\n"
                                       "Lorem Ipsum is simply dummy text of the printing and typesetting industry. "
                                       "Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, "
                                       "when an unknown printer took a galley of type and scrambled it to make a"
                                       "type specimen book. It has survived not only five centuries, but also the leap "
                                       "into electronic typesetting, remaining essentially unchanged. "
                                       "It was popularised in the 1960s with the release of Letraset sheets containing "
                                       "Lorem Ipsum passages, and more recently with desktop publishing software "
                                       "like Aldus PageMaker including versions of Lorem Ipsum.")
    await context.bot.send_photo(query.message.chat_id,
                                 "https://ss7.vzw.com/is/image/VerizonWireless/zagg-invisibleshield-glass-elite-visionguard-screen-protector-for-leonardo-zag200108321-v-iset")
    return ConversationHandler.END


def main():
    application = Application.builder().token(CONSTANTS.get("CONSTANTS", "ORDER_DISPATCHER_BOT_TOKEN")).build()

    start_handler = CommandHandler("start", start)

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("faq", faq)],
        states={
            START_ROUTE: [
                CallbackQueryHandler(computer, "^" + str(COMPUTER) + "$"),
                CallbackQueryHandler(phone, "^" + str(PHONE) + "$"),
            ],
            COMPUTER: [
                CallbackQueryHandler(start_over, "^" + str(COMPUTER_START_OVER) + "$"),
                CallbackQueryHandler(computer_screen, "^" + str(COMPUTER_SCREEN) + "$")
            ],
            PHONE: [
                CallbackQueryHandler(start_over, "^" + str(PHONE_START_OVER) + "$"),
                CallbackQueryHandler(phone_screen, "^" + str(PHONE_SCREEN) + "$")
            ]
        },
        fallbacks=[CommandHandler("start", start)]
    )

    application.add_handler(start_handler)
    application.add_handler(conversation_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
