from configparser import ConfigParser
import logging
from pprint import pformat

from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    KeyboardButton
)
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

logger_qa = logging.getLogger(__name__)


# States for /faq Conversation
DEVICE_OS, DEVICE, DEVICE_COMPUTER, DEVICE_COMPUTER_SCREEN, DEVICE_PHONE = range(5)
APPLE, ANDROID_LINUX, WINDOWS = range(3)
DEVICE_START_OVER, COMPUTER, PHONE = range(3)

COMPUTER_START_OVER, COMPUTER_SCREEN, COMPUTER_KEYBOARD, COMPUTER_PROCESSOR, COMPUTER_GRAPHIC_CARD = range(5)
COMPUTER_SCREEN_START_OVER, COMPUTER_SCREEN_P1 = range(2)

PHONE_START_OVER, PHONE_SCREEN, PHONE_KEYBOARD, PHONE_PROCESSOR, PHONE_GRAPHIC_CARD = range(5)

# States for /forward Conversation
FORWARD_PAGE_1, FORWARD_PAGE_2, FORWARD_PAGE_3 = range(3)


async def apple(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt same text & keyboard as `faq` does but not as new message"""
    logger_qa.info("apple()")
    context.user_data["Device_Context"]["Device_OS_Brand"] = "Apple / iOS"
    logger_qa.info("context.user_data: {}".format(pformat(context.user_data)))

    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton(text="Computer", callback_data=COMPUTER),
         InlineKeyboardButton(text="Phone", callback_data=PHONE)]
    ]
    inline_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("Select a device", reply_markup=inline_markup)

    return DEVICE


async def android_linux(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt same text & keyboard as `faq` does but not as new message"""
    logger_qa.info("android_linux()")
    context.user_data["Device_Context"]["Device_OS_Brand"] = "Android / Linux"
    logger_qa.info("context.user_data: {}".format(pformat(context.user_data)))

    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton(text="Computer", callback_data=COMPUTER),
         InlineKeyboardButton(text="Phone", callback_data=PHONE)]
    ]
    inline_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("Select a device", reply_markup=inline_markup)

    return DEVICE


async def windows(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """WINDOWS"""
    logger_qa.info("windows()")
    context.user_data["Device_Context"]["Device_OS_Brand"] = "Windows"
    logger_qa.info("context.user_data: {}".format(pformat(context.user_data)))

    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton(text="Computer", callback_data=COMPUTER),
         InlineKeyboardButton(text="Phone", callback_data=PHONE)]
    ]
    inline_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("Select a device", reply_markup=inline_markup)

    return DEVICE


async def computer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stuff"""
    logger_qa.info("computer()")
    context.user_data["Device_Context"]["Device"] = "Computer"
    logger_qa.info("context.user_data: {}".format(pformat(context.user_data)))

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

    return DEVICE_COMPUTER


async def computer_screen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons. This is the end point of the conversation."""
    logger_qa.info("computer_screen()")
    context.user_data["Device_Context"]["Part"] = "Screen"
    logger_qa.info("context.user_data: {}".format(pformat(context.user_data)))

    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton(text="Computer Screen P1", callback_data=COMPUTER_SCREEN),
         InlineKeyboardButton(text="Computer Screen P2", callback_data=COMPUTER_KEYBOARD)],
        [InlineKeyboardButton(text="Computer Screen P3", callback_data=COMPUTER_PROCESSOR),
         InlineKeyboardButton(text="Computer Screen P4", callback_data=COMPUTER_GRAPHIC_CARD)],
        [InlineKeyboardButton(text="<< BACK", callback_data=COMPUTER_SCREEN_START_OVER)]
    ]
    inline_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text="Select a component", reply_markup=inline_markup)

    return DEVICE_COMPUTER_SCREEN


async def computer_screen_p1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """STUFF"""
    logger_qa.info("computer_screen_p1()")
    context.user_data["Device_Context"]["Problem"] = "Broken Screen"
    logger_qa.info("context.user_data: {}".format(pformat(context.user_data)))
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


async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stuff"""
    logger_qa.info("phone()")
    context.user_data["Device_Context"]["Device"] = "Phone"
    logger_qa.info("context.user_data: {}".format(pformat(context.user_data)))

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
    logger_qa.info("phone_screen()")
    context.user_data["Device_Context"]["Part"] = "Screen"
    logger_qa.info("context.user_data: {}".format(pformat(context.user_data)))

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
                                 "AgACAgQAAxkBAAEaA5pjdOcrgVo49SOVfjOGoKWDQU5ejAACLa8xG_6apVMGam1ZdlbEYwEAAwIAA3MAAysE")
    return ConversationHandler.END