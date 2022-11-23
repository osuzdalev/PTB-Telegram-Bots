import sys

from SqliteBasePersistence import SqliteBasePersistence
from telegram_database import *
import helpers
from qa import *

# Enable logging
logging.basicConfig(
    #format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    format="[%(asctime)s] {%(name)s:%(lineno)d} %(levelname)s - %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# States for /forward Conversation
FORWARD_PAGE_1, FORWARD_PAGE_2, FORWARD_PAGE_3 = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stuff"""
    logger.info("start()")
    user = update.message.from_user
    logger.info("Bot started by user {}".format(user.username))
    insert_new_customer(user.id, user.username, user.first_name, user.last_name)

    context.user_data["Device_Context"] = None

    await update.message.reply_text("Welcome!\n"
                                    "/faq - find an easy fix\n"
                                    "/request - contact customer service")


async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stuff"""
    logger.info("faq()")
    device_context = {"Device_OS_Brand": '', "Device": '', "Part": '', "Problem": ''}
    context.user_data["Device_Context"] = device_context

    keyboard = [
        [InlineKeyboardButton(text="Apple/iOS", callback_data=APPLE)],
        [InlineKeyboardButton(text="Android / Linux", callback_data=ANDROID_LINUX),
         InlineKeyboardButton(text="Windows", callback_data=WINDOWS)]
    ]
    inline_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Select a Brand/OS", reply_markup=inline_markup)

    return DEVICE_OS


async def faq_start_over(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt same text & keyboard as `faq` does but not as new message"""
    logger.info("faq_start_over()")
    device_context = {"Device_OS_Brand": '', "Device": '', "Part": '', "Problem": ''}
    context.user_data["Device_Context"] = device_context

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

    await query.edit_message_text("Select a Brand/OS", reply_markup=inline_markup)

    return DEVICE_OS


async def request(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Checks if Customer's PhoneNumber is in Database before sending request to Customer Service
    if not asks for contact details permission and then sends a CONTACT message to bot"""
    logger.info("request()")
    try:
        phone_number = get_customer_data(update.effective_user.id)[-1]
        await reach_customer_service(update, _, phone_number)
    except (TypeError, AttributeError) as e:
        contact_button = KeyboardButton(text="send_contact", request_contact=True)
        contact_keyboard = [[contact_button]]
        reply_markup = ReplyKeyboardMarkup(contact_keyboard, one_time_keyboard=True)

        await update.message.reply_text(text="Contacting customer service, please share your contact details",
                                        reply_markup=reply_markup)


async def reach_customer_service(update: Update, context: ContextTypes.DEFAULT_TYPE, phone_number: int = None) -> None:
    """Stuff"""
    logger.info("reach_customer_service()")
    user = update.message.from_user
    user_data = [user.id, user.name, user.first_name, user.last_name]

    # Check if PhoneNumber already in Database
    if phone_number is None:
        phone_number = update.message.contact.phone_number

    insert_customer_phone_number(user.id, phone_number)

    try:
        device_context = context.user_data["Device_Context"]
    except KeyError:
        logger.info("Empty device_context")
        device_context = {"Device_OS_Brand": '', "Device": '', "Part": '', "Problem": ''}

    insert_new_order(user.id, device_context)
    OrderID = get_customer_last_OrderID(user.id)

    order_message_str = helpers.get_order_message_str(OrderID, user_data, device_context, phone_number)

    await context.bot.sendMessage(CONSTANTS.get("TELEGRAM_ID", "USER_ID_FR"), order_message_str)

    await update.message.reply_text("Customer service will contact you", reply_markup=ReplyKeyboardRemove())


async def take(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """(Conceptual) Contractor confirms he is taking the order"""
    logger.info("take()")
    order_message_id = update.effective_message.message_id - 1
    logger.info("chat_data: {}".format(context.chat_data))


async def forward(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Contractor command: opens Converstation to select which ContractorID to send current Order to"""
    logger.info("forward()")
    # Save current OrderID in the user_data
    context.bot_data["Current Order"] = context.args[0]

    keyboard = [
        [InlineKeyboardButton(text="Oleg (Fr)", callback_data=CONSTANTS.get("TELEGRAM_ID", "USER_ID_MAIN")),
         InlineKeyboardButton(text="Oleg (Fr)", callback_data=CONSTANTS.get("TELEGRAM_ID", "USER_ID_MAIN"))],
        [InlineKeyboardButton(text="NEXT >>", callback_data=FORWARD_PAGE_2)],
    ]
    inline_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Select Contractor", reply_markup=inline_markup)

    return FORWARD_PAGE_1


async def forward_page_1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """First page of the /forward Inline Menu as a Callback Query"""
    logger.info("forward_page_1()")

    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton(text="Oleg (Fr)", callback_data=CONSTANTS.get("TELEGRAM_ID", "USER_ID_MAIN")),
         InlineKeyboardButton(text="Oleg (Fr)", callback_data=CONSTANTS.get("TELEGRAM_ID", "USER_ID_MAIN"))],
        [InlineKeyboardButton(text="NEXT >>", callback_data=FORWARD_PAGE_2)],
    ]
    inline_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("Select Contractor", reply_markup=inline_markup)

    return FORWARD_PAGE_1


async def forward_page_2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Second page of the /forward Inline Menu"""
    logger.info("forward_page_2()")

    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton(text="Oleg (Fr)", callback_data=CONSTANTS.get("TELEGRAM_ID", "USER_ID_MAIN")),
         InlineKeyboardButton(text="Oleg (Fr)", callback_data=CONSTANTS.get("TELEGRAM_ID", "USER_ID_MAIN"))],
        [InlineKeyboardButton(text="<< PREVIOUS", callback_data=FORWARD_PAGE_1),
         InlineKeyboardButton(text="NEXT >>", callback_data=FORWARD_PAGE_3)],
    ]
    inline_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("Select Contractor", reply_markup=inline_markup)

    return FORWARD_PAGE_2


async def forward_page_3(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Third page of the /forward Inline Menu"""
    logger.info("forward_page_3()")

    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton(text="Oleg (Fr)", callback_data=CONSTANTS.get("TELEGRAM_ID", "USER_ID_MAIN")),
         InlineKeyboardButton(text="Oleg (Fr)", callback_data=CONSTANTS.get("TELEGRAM_ID", "USER_ID_MAIN"))],
        [InlineKeyboardButton(text="<< PREVIOUS", callback_data=FORWARD_PAGE_2)],
    ]
    inline_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("Select Contractor", reply_markup=inline_markup)

    return FORWARD_PAGE_3


async def forward_to_contractor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ContractID in current Order is changed to new contractor selected
    then Order details are sent as a message to Contractor"""
    logger.info("forward_to_contractor()")

    query = update.callback_query
    await query.answer()

    # Order
    order_data = get_order_data(context.bot_data["Current Order"])
    OrderID = order_data[0]

    # Change the ContractID for the Order
    contractor_data = get_contractor_data(int(query.data))
    ContractorID = contractor_data[0]
    update_order_ContractID(OrderID, ContractorID)

    # Customer
    customer_data = get_customer_data(order_data[1])
    customer_phone_number = customer_data[-1]

    order_message_str = helpers.get_order_message_str(OrderID, customer_data, order_data, customer_phone_number)

    await context.bot.sendMessage(ContractorID, order_message_str)

    await query.edit_message_text("Order passed to \n{}\n{}\n{}\n{}"
                                  .format(contractor_data[1], contractor_data[2], contractor_data[3], contractor_data[4]))

    return ConversationHandler.END


def main():
    sqlite_base_persistence = SqliteBasePersistence()
    sqlite_base_persistence.connect_database(CONSTANTS.get("ORDER_DISPATCHER_BOT", "DATABASE_FILEPATH"))

    application = Application.builder() \
        .token(CONSTANTS.get("ORDER_DISPATCHER_BOT", "TOKEN"))\
        .persistence(persistence=sqlite_base_persistence)\
        .build()

    faq_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("faq", faq)],
        states={
            DEVICE_OS: [
                CallbackQueryHandler(apple, "^" + str(APPLE) + "$"),
                CallbackQueryHandler(android_linux, "^" + str(ANDROID_LINUX) + "$"),
                CallbackQueryHandler(windows, "^" + str(WINDOWS) + "$")
            ],
            DEVICE: [
                CallbackQueryHandler(faq_start_over, "^" + str(DEVICE_START_OVER) + "$"),
                CallbackQueryHandler(computer, "^" + str(COMPUTER) + "$"),
                CallbackQueryHandler(phone, "^" + str(PHONE) + "$")
            ],
            DEVICE_COMPUTER: [
                CallbackQueryHandler(faq_start_over, "^" + str(COMPUTER_START_OVER) + "$"),
                CallbackQueryHandler(computer_screen, "^" + str(COMPUTER_SCREEN) + "$")
            ],
            DEVICE_COMPUTER_SCREEN: [
                CallbackQueryHandler(faq_start_over, "^" + str(COMPUTER_SCREEN_START_OVER) + "$"),
                CallbackQueryHandler(computer_screen_p1, "^" + str(COMPUTER_SCREEN_P1) + "$")
            ],
            DEVICE_PHONE: [
                CallbackQueryHandler(faq_start_over, "^" + str(PHONE_START_OVER) + "$"),
                CallbackQueryHandler(phone_screen, "^" + str(PHONE_SCREEN) + "$")
            ]
        },
        fallbacks=[CommandHandler("start", start)]
    )

    start_handler = CommandHandler("start", start)
    # start_contractor_handler = CommandHandler("start_contractor", start_contractor)
    request_handler = CommandHandler("request", request)
    contact_handler = MessageHandler(filters.CONTACT, reach_customer_service)
    take_handler = CommandHandler("take", take)

    forward_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("forward", forward)],
        states={
            FORWARD_PAGE_1: [
                CallbackQueryHandler(forward_to_contractor, r"\d{8,10}"),
                CallbackQueryHandler(forward_page_2, "^" + str(FORWARD_PAGE_2) + "$")
            ],
            FORWARD_PAGE_2: [
                CallbackQueryHandler(forward_to_contractor, r"\d{8,10}"),
                CallbackQueryHandler(forward_page_1, "^" + str(FORWARD_PAGE_1) + "$"),
                CallbackQueryHandler(forward_page_3, "^" + str(FORWARD_PAGE_3) + "$")
            ],
            FORWARD_PAGE_3: [
                CallbackQueryHandler(forward_to_contractor, r"\d{8,10}"),
                CallbackQueryHandler(forward_page_2, "^" + str(FORWARD_PAGE_2) + "$")
            ],
        },
        fallbacks=[CommandHandler("start", start)]
    )

    application.add_handler(start_handler)
    # application.add_handler(start_contractor_handler)
    application.add_handler(faq_conversation_handler)
    application.add_handler(request_handler)
    application.add_handler(contact_handler)
    application.add_handler(take_handler)
    application.add_handler(forward_conversation_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
