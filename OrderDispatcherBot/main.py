from configparser import ConfigParser
import logging
from pprint import pformat
import sys

from telegram import ReplyKeyboardMarkup, Update, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, KeyboardButton
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

DEVICE_OS, DEVICE, DEVICE_COMPUTER, DEVICE_COMPUTER_SCREEN, DEVICE_PHONE = range(5)
DEVICE_START_OVER, COMPUTER, PHONE = range(3)
COMPUTER_START_OVER, COMPUTER_SCREEN, COMPUTER_KEYBOARD, COMPUTER_PROCESSOR, COMPUTER_GRAPHIC_CARD = range(5)
COMPUTER_SCREEN_START_OVER, COMPUTER_SCREEN_P1 = range(2)
PHONE_START_OVER, PHONE_SCREEN, PHONE_KEYBOARD, PHONE_PROCESSOR, PHONE_GRAPHIC_CARD = range(5)
APPLE, ANDROID_LINUX, WINDOWS = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stuff"""
    user = update.message.from_user
    logger.info("Bot started by user {}".format(user.username))
    logger.info(update.message.from_user)
    context.user_data["Device_Context"] = None

    await update.message.reply_text("Welcome!\n"
                                    "/faq - find an easy fix\n"
                                    "/request - contact customer service")


async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stuff"""
    logger.info("faq()")
    device_context = {"Device_OS_Brand": '', "Device": '', "Part": '', "Problem": ''}
    context.user_data["Device_Context"] = device_context
    logger.info("context.user_data: {}".format(pformat(context.user_data)))

    keyboard = [
        [InlineKeyboardButton(text="Apple/iOS", callback_data=APPLE)],
        [InlineKeyboardButton(text="Android / Linux", callback_data=ANDROID_LINUX),
         InlineKeyboardButton(text="Windows", callback_data=WINDOWS)]
    ]
    inline_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Select a Brand/OS", reply_markup=inline_markup)

    return DEVICE_OS


async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt same text & keyboard as `faq` does but not as new message"""
    logger.info("start_over()")
    device_context = {"Device_OS_Brand": '', "Device": '', "Part": '', "Problem": ''}
    context.user_data["Device_Context"] = device_context
    logger.info("context.user_data: {}".format(pformat(context.user_data)))

    # Get CallbackQuery from Update
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()
    keyboard = [
        [InlineKeyboardButton(text="Apple/iOS", callback_data=APPLE)],
        [InlineKeyboardButton(text="Android / Linux", callback_data=ANDROID_LINUX),
         InlineKeyboardButton(text="Windows", callback_data=WINDOWS)]
    ]
    inline_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Select a Brand/OS", reply_markup=inline_markup)

    return DEVICE_OS


async def apple(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt same text & keyboard as `faq` does but not as new message"""
    logger.info("apple()")
    context.user_data["Device_Context"]["Device_OS_Brand"] = "Apple / iOS"
    logger.info("context.user_data: {}".format(pformat(context.user_data)))

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
    logger.info("android_linux()")
    context.user_data["Device_Context"]["Device_OS_Brand"] = "Android / Linux"
    logger.info("context.user_data: {}".format(pformat(context.user_data)))

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
    logger.info("windows()")
    context.user_data["Device_Context"]["Device_OS_Brand"] = "Windows"
    logger.info("context.user_data: {}".format(pformat(context.user_data)))

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
    logger.info("computer()")
    context.user_data["Device_Context"]["Device"] = "Computer"
    logger.info("context.user_data: {}".format(pformat(context.user_data)))

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
    logger.info("computer_screen()")
    context.user_data["Device_Context"]["Part"] = "Screen"
    logger.info("context.user_data: {}".format(pformat(context.user_data)))

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
    logger.info("computer_screen_p1()")
    context.user_data["Device_Context"]["Problem"] = "Broken Screen"
    logger.info("context.user_data: {}".format(pformat(context.user_data)))
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
    logger.info("phone()")
    context.user_data["Device_Context"]["Device"] = "Phone"
    logger.info("context.user_data: {}".format(pformat(context.user_data)))

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
    context.user_data["Device_Context"]["Part"] = "Screen"
    logger.info("context.user_data: {}".format(pformat(context.user_data)))

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


async def request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt same text & keyboard as `faq` does but not as new message"""
    logger.info("request()")

    contact_keyboard = KeyboardButton(text="send_contact", request_contact=True)
    custom_keyboard = [[contact_keyboard]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True)

    await update.message.reply_text(text="Contacting customer service, please share your contact details",
                                    reply_markup=reply_markup)


async def reach_customer_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stuff"""
    logger.info("reach_customer_service()")
    contact = update.message.contact.to_dict()
    user = update.message.from_user.to_dict()

    user_info = '@' + user["username"] + '\n' + \
                contact["first_name"] + '\n' + contact["last_name"] + '\n' + contact["phone_number"]

    device_context = context.user_data["Device_Context"]
    try:
        device_info = device_context["Device_OS_Brand"] + '\n' + device_context["Device"] + '\n' + device_context["Part"]\
                      + '\n' + device_context["Problem"]
    except TypeError:
        logger.info("Empty device_context")
        device_info = ""

    await context.bot.sendMessage(CONSTANTS.get("CONSTANTS", "USER_ID_FR"),
                                  "Customer service required\n\n{}\n\n{}".format(user_info, device_info))

    await update.message.reply_text("Customer service will contact you")


def main():
    application = Application.builder().token(CONSTANTS.get("CONSTANTS", "ORDER_DISPATCHER_BOT_TOKEN")).build()

    start_handler = CommandHandler("start", start)

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("faq", faq)],
        states={
            DEVICE_OS: [
                CallbackQueryHandler(apple, "^" + str(APPLE) + "$"),
                CallbackQueryHandler(android_linux, "^" + str(ANDROID_LINUX) + "$"),
                CallbackQueryHandler(windows, "^" + str(WINDOWS) + "$")
            ],
            DEVICE: [
                CallbackQueryHandler(start_over, "^" + str(DEVICE_START_OVER) + "$"),
                CallbackQueryHandler(computer, "^" + str(COMPUTER) + "$"),
                CallbackQueryHandler(phone, "^" + str(PHONE) + "$")
            ],
            DEVICE_COMPUTER: [
                CallbackQueryHandler(start_over, "^" + str(COMPUTER_START_OVER) + "$"),
                CallbackQueryHandler(computer_screen, "^" + str(COMPUTER_SCREEN) + "$")
            ],
            DEVICE_COMPUTER_SCREEN: [
                CallbackQueryHandler(start_over, "^" + str(COMPUTER_SCREEN_START_OVER) + "$"),
                CallbackQueryHandler(computer_screen_p1, "^" + str(COMPUTER_SCREEN_P1) + "$")
            ],
            DEVICE_PHONE: [
                CallbackQueryHandler(start_over, "^" + str(PHONE_START_OVER) + "$"),
                CallbackQueryHandler(phone_screen, "^" + str(PHONE_SCREEN) + "$")
            ]
        },
        fallbacks=[CommandHandler("start", start)]
    )

    request_handler = CommandHandler("request", request)
    contact_handler = MessageHandler(filters.CONTACT, reach_customer_service)

    application.add_handler(start_handler)
    application.add_handler(conversation_handler)
    application.add_handler(request_handler)
    application.add_handler(contact_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
