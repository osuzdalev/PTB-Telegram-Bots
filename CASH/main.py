import logging
from typing import Dict
import pickle
import os.path
from pprint import pformat
import sys

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    PicklePersistence,
)

from config import *

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY = range(2)
ORDER_NUMBER, EDITING_TEXT = range(2)

start_keyboard = [["/start"]]
start_markup = ReplyKeyboardMarkup(start_keyboard)

main_keyboard = [
    ["Адрес", "Номер Телефона", "Источник", "Работа"],
    ["Сумма"],
    ["Завершить"],
]
main_markup = ReplyKeyboardMarkup(main_keyboard)

source_keyboard = [
    ["Яндекс", "Авито"],
    ["Профи", "по Рекомендации"],
]
source_markup = ReplyKeyboardMarkup(source_keyboard)

edit_keyboard = [["❌", "✅"]]
edit_markup = ReplyKeyboardMarkup(edit_keyboard)


def write_source_pickle(cash_data_path: str) -> None:
    with open(cash_data_path, 'wb') as handle:
        db = {'conversations': {}, 'user_data': {},
              'chat_data': {}, 'bot_data': {}, 'callback_data': ([], {})}
        pickle.dump(db, handle, protocol=pickle.HIGHEST_PROTOCOL)


def check_database(cash_data_path: str) -> None:
    db_ready = None

    if os.path.isfile(cash_data_path):
        with open(cash_data_path, "rb") as handle:
            db = pickle.load(handle)
            db_ready = True if all(datas in db for datas in
                                   ["conversations", "user_data", "chat_data", "bot_data", "callback_data"]) else False
    elif not os.path.isfile(cash_data_path):
        write_source_pickle(cash_data_path)
    elif os.path.isfile(cash_data_path) and not db_ready:
        write_source_pickle(cash_data_path)

    with open(cash_data_path, "rb") as handle:
        db = pickle.load(handle)
        logger.info("DATA AFTER CHECKING: {}".format(pformat(db)))


async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("EDIT, USER DATA: {}\nCHAT DATA: {}".format(context.user_data, context.chat_data))

    reply = await update.message.reply_text("Номер заказа который хотите поменять")
    context.chat_data["message_to_delete_ids"] += [update.message.id, reply.id]

    return ORDER_NUMBER


async def get_order_to_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("GET_ORDER_TO_EDIT, USER DATA: {}\nCHAT DATA: {}".format(context.user_data, context.chat_data))

    # Set the order cursor to the one you want to edit
    context.chat_data["current_order"] = int(update.message.text)

    reply = await update.message.reply_text("Отправьте новый текст", reply_markup=edit_markup)
    context.chat_data["message_to_delete_ids"] += [update.message.id, reply.id]

    return EDITING_TEXT


async def write_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("WRITE_EDIT, USER DATA: {}\nCHAT DATA: {}".format(context.user_data, context.chat_data))

    text = update.effective_message.text
    logger.info("EDITED TEXT RECEIVED: {}".format(text))

    order_number = context.chat_data["current_order"]
    context.user_data[order_number]["Edited Text"] = text

    reply = await update.message.reply_text("Новый Текст, все верно?\n{}".format(text), reply_markup=edit_markup)
    context.chat_data["message_to_delete_ids"] += [update.message.id, reply.id]

    return EDITING_TEXT


async def commit_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("COMMIT_EDIT, USER DATA: {}\nCHAT DATA: {}".format(context.user_data, context.chat_data))

    if update.message.text == "✅":
        order_number = context.chat_data["current_order"]
        order_message_id = context.chat_data["orders_message_ids"][order_number]
        logger.info("order_message_id: {}".format(order_message_id))

        edited_text = context.user_data[order_number]["Edited Text"]
        final_text = "#{}\n".format(order_number) + edited_text

        await context.bot.editMessageText(final_text, chat_id=update.effective_chat.id, message_id=order_message_id)

    # Cleanup
    for i in context.chat_data["message_to_delete_ids"]:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=i)
    context.chat_data["message_to_delete_ids"] = []
    await update.effective_message.delete()

    return ConversationHandler.END


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clears all of user and chat data, deletes order message"""
    logger.info("CLEAR, USER DATA: {}\nCHAT DATA: {}".format(context.user_data, context.chat_data))
    # check if dict are empty, if not delete messages
    if all(k in context.chat_data for k in ["orders_message_ids", "message_to_delete_ids"]):
        for k, v in context.chat_data["orders_message_ids"].items():
            message_id = context.chat_data["orders_message_ids"][k]
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)
        for i in range(len(context.chat_data["message_to_delete_ids"])):
            message_id = context.chat_data["message_to_delete_ids"][i]
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)

    await update.effective_message.delete()


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clears all of user and chat data, deletes order message"""
    logger.info("RESET, USER DATA: {}\nCHAT DATA: {}".format(context.user_data, context.chat_data))
    # clear messages first
    await clear(update, context)

    context.user_data.clear()
    context.chat_data.clear()
    context.chat_data["current_order"] = 0

    logger.info("USER DATA AFTER /reset: {}".format(pformat(context.user_data)))
    logger.info("CHAT DATA AFTER /reset: {}".format(pformat(context.chat_data)))


async def data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("DATA, USER DATA: {}\nCHAT DATA: {}".format(context.user_data, context.chat_data))

    await update.effective_message.delete()


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("UNKNOWN, USER DATA: {}\nCHAT DATA: {}".format(context.user_data, context.chat_data))
    reply_id = await update.message.reply_text("wrong command")

    await update.effective_message.delete()
    await reply_id.delete()


def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f"{value}" for key, value in user_data.items()]
    return "\n".join(facts).join(["\n", "\n"])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation, initiates the DB and ask user for input."""
    logger.info("START, USER DATA: {}\nCHAT DATA: {}".format(context.user_data, context.chat_data))

    # Checking order_# and updating it
    if all(i in context.chat_data for i in ["current_order", "message_to_delete_ids", "orders_message_ids"]):
        logger.info("NEW START")
        context.chat_data["current_order"] = max(context.user_data) + 1
        current_order = context.chat_data["current_order"]
        context.user_data[current_order] = {"choice": ""}
        context.chat_data["message_to_delete_ids"] = []
    else:
        logger.info("FIRST INITIALIZATION")
        context.chat_data["current_order"] = 0
        current_order = context.chat_data["current_order"]
        context.user_data[current_order] = {"choice": ""}
        context.chat_data["message_to_delete_ids"] = []
        context.chat_data["orders_message_ids"] = {}
        logger.info("CHAT DATA: {}".format(pformat(context.chat_data)))

    reply_message_id = await update.message.reply_text(text="Новый заказ", reply_markup=main_markup)

    context.chat_data["message_to_delete_ids"] += [update.effective_message.id, reply_message_id.id]

    return CHOOSING


async def source(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Choose one of the options for source in the Reply Keyboard and get back to regular choices"""
    logger.info("SOURCE, USER DATA: {}\nCHAT DATA: {}".format(context.user_data, context.chat_data))

    # initiate dict cursor
    text = update.message.text
    current_order = context.chat_data["current_order"]
    context.user_data[current_order]["choice"] = text

    reply_message_id = await update.message.reply_text(text="Источник: ", reply_markup=source_markup)

    context.chat_data["message_to_delete_ids"] += [update.effective_message.id, reply_message_id.id]

    return TYPING_REPLY


async def regular_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for info about the selected predefined choice."""
    logger.info("REGULAR_CHOICE, USER DATA: {}\nCHAT DATA: {}".format(context.user_data, context.chat_data))

    # initiate dict cursor
    text = update.message.text
    current_order = context.chat_data["current_order"]
    context.user_data[current_order]["choice"] = text

    reply_message_id = await update.message.reply_text(f"Напишите {text.lower()}")

    context.chat_data["message_to_delete_ids"] += [update.effective_message.id, reply_message_id.id]

    return TYPING_REPLY


async def received_information(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store info provided by user and ask for the next category."""
    logger.info("RECEIVED_INFORMATION, USER DATA: {}\nCHAT DATA: {}".format(context.user_data, context.chat_data))

    current_order_number = context.chat_data["current_order"]
    current_order = context.user_data[current_order_number]

    # Initiating cursor
    text = update.message.text
    category = current_order["choice"]

    # Placing data
    current_order[category] = text

    # Removing cursor
    del current_order["choice"]

    reply_message_id = await update.message.reply_text(f"{facts_to_str(current_order)}", reply_markup=main_markup)

    context.chat_data["message_to_delete_ids"] += [update.effective_message.id, reply_message_id.id]

    return CHOOSING


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    logger.info("DONE, USER DATA: {}\nCHAT DATA: {}".format(context.user_data, context.chat_data))

    current_order_number = context.chat_data["current_order"]
    current_order = context.user_data[current_order_number]
    if "choice" in current_order:
        del current_order["choice"]

    order_message = await update.message.reply_text("#{}{}".format(current_order_number, facts_to_str(current_order)))

    logger.info("order_message.id: {}".format(order_message.message_id))

    context.chat_data["message_to_delete_ids"] += [update.effective_message.id]

    for i in context.chat_data["message_to_delete_ids"]:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=i)

    context.chat_data["orders_message_ids"][current_order_number] = order_message.id
    context.chat_data["message_to_delete_ids"] = []

    return ConversationHandler.END


def main() -> None:
    pickle_persistence = PicklePersistence(filepath=CASH_DATA_PATH)
    application = Application.builder().token(CASH_BOT_TOKEN).persistence(persistence=pickle_persistence).build()

    # Add conversation handler with the states CHOOSING and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex("^(Адрес|Номер Телефона|Работа|Сумма)$"), regular_choice),
                MessageHandler(filters.Regex("^Источник$"), source),
            ],
            TYPING_REPLY: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Завершить")), received_information,)
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Завершить"), done)],
    )

    # Add conversation handler with the states ORDER_NUMBER and TYPING_REPLY
    edit_handler = ConversationHandler(
        entry_points=[CommandHandler("edit", edit)],
        states={
            ORDER_NUMBER: [MessageHandler(filters.Regex(r"\d*"), get_order_to_edit)],
            EDITING_TEXT: [
                MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^(❌|✅)")), write_edit)
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^(❌|✅)"), commit_edit)],
    )

    application.add_handler(conv_handler)
    application.add_handler(edit_handler)

    order_handler = CommandHandler("reset", reset)
    data_handler = CommandHandler("data", data)
    clear_handler = CommandHandler("clear", clear)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(order_handler)
    application.add_handler(data_handler)
    application.add_handler(clear_handler)
    application.add_handler(unknown_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    check_database(CASH_DATA_PATH)
    main()
