import logging
from typing import Dict
import pickle

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
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY = range(2)

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


def check_database(cash_data_path: str) -> None:
    db_ready = None

    with open(cash_data_path, "rb") as handle:
        data = pickle.load(handle)
        print("Opening data: ", data)
        db_ready = True if "current_order" in data["user_data"][USER_ID] else False

    if not db_ready:
        with open(cash_data_path, 'wb') as handle:
            data = {'conversations': {}, 'user_data': {USER_ID: {"current_order": 0}},
                    'chat_data': {USER_ID: {}}, 'bot_data': {}, 'callback_data': ([], {})}
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(cash_data_path, "rb") as handle:
            data = pickle.load(handle)
            print("Data after checking: ", data)


async def reset(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Deletes all of user and chat data"""
    _.user_data.clear()
    _.chat_data.clear()
    _.user_data["current_order"] = 0

    await update.effective_message.delete()


async def data(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    print("USER DATA: ", _.user_data)
    print("CHAT DATA: ", _.chat_data)

    await update.effective_message.delete()


async def unknown(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    reply_id = await update.message.reply_text("wrong command")

    await update.effective_message.delete()
    await reply_id.delete()


def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f"{value}" for key, value in user_data.items()]
    return "\n".join(facts).join(["\n", "\n"])


async def start(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation, initiates the DB and ask user for input."""
    # Checking order_# and updating it
    if not (0 in _.user_data):
        _.user_data[0] = {}
    else:
        _.user_data["current_order"] = _.user_data["current_order"] + 1
        _.user_data[_.user_data["current_order"]] = {"choice": ""}

    reply_message_id = await update.message.reply_text(text="Новый заказ", reply_markup=main_markup)

    _.chat_data["message_to_delete_ids"] = []
    _.chat_data["message_to_delete_ids"] += [update.effective_message.id, reply_message_id.id]

    return CHOOSING


async def source(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    """Choose one of the options for source in the Reply Keyboard and get back to regular choices"""

    # initiate dict cursor
    text = update.message.text
    _.user_data[_.user_data["current_order"]]["choice"] = text

    reply_message_id = await update.message.reply_text(text="Источник: ", reply_markup=source_markup)

    _.chat_data["message_to_delete_ids"] += [update.effective_message.id, reply_message_id.id]

    return TYPING_REPLY


async def regular_choice(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for info about the selected predefined choice."""
    # initiate dict cursor
    text = update.message.text
    _.user_data[_.user_data["current_order"]]["choice"] = text

    reply_message_id = await update.message.reply_text(f"Напишите {text.lower()}")

    _.chat_data["message_to_delete_ids"] += [update.effective_message.id, reply_message_id.id]

    return TYPING_REPLY


async def received_information(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    """Store info provided by user and ask for the next category."""
    current_order = _.user_data[_.user_data["current_order"]]
    # Initiating cursor
    text = update.message.text
    category = current_order["choice"]

    # Placing data
    current_order[category] = text

    # Removing cursor
    del current_order["choice"]

    reply_message_id = await update.message.reply_text(f"{facts_to_str(current_order)}", reply_markup=main_markup)

    _.chat_data["message_to_delete_ids"] += [update.effective_message.id, reply_message_id.id]

    return CHOOSING


async def done(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    current_order = _.user_data[_.user_data["current_order"]]
    if "choice" in current_order:
        del current_order["choice"]

    _.chat_data["message_to_delete_ids"] += [update.effective_message.id]

    for m in _.chat_data["message_to_delete_ids"]:
        await _.bot.delete_message(update.effective_chat.id, m)

    await update.message.reply_text("#{}{}".format(_.user_data["current_order"], facts_to_str(current_order)),
                                    reply_markup=start_markup)

    return ConversationHandler.END


def main() -> None:
    pickle_persistence = PicklePersistence(filepath=CASH_DATA_PATH)
    application = Application.builder().token(TOKEN).persistence(persistence=pickle_persistence).build()

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

    order_handler = CommandHandler("reset", reset)
    data_handler = CommandHandler("data", data)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(conv_handler)
    application.add_handler(order_handler)
    application.add_handler(data_handler)
    application.add_handler(unknown_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    check_database(CASH_DATA_PATH)
    main()
