from collections import Counter

import logging
from telegram import ReplyKeyboardMarkup, Update, constants
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

from config import *
from db import BotDB


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BotDB = BotDB('Departure_DB.db')

keyboard = ReplyKeyboardMarkup([['❌', '🟠', '✅'], ['✏️', '📊', '📖']])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="INITIALISING", reply_markup=keyboard)


def add_departure(value):
    if value == "❌":
        BotDB.add_departure(0)
        answer = '✅ Departure successfully added to database <b>(❌ BAD)</b>'
    elif value == "🟠":
        BotDB.add_departure(1)
        answer = '✅ Departure successfully added to database <b>(🟠 NEUTRAL)</b>'
    elif value == "✅":
        BotDB.add_departure(2)
        answer = '✅ Departure successfully added to database <b>(✅ GOOD)</b>'

    return answer


def get_stats():
    stats = BotDB.get_departure_stats()
    counts = Counter(elem[0] for elem in stats)

    answer = f"<b>|      |          TOTAL            |            %            |</b>\n"
    answer += f" ❌                {counts[0]}                           {round(counts[0] * 100 / len(stats), 2)}\n"
    answer += f" 🟠                {counts[1]}                           {round(counts[1] * 100 / len(stats), 2)}\n"
    answer += f" ✅                {counts[2]}                           {round(counts[2] * 100 / len(stats), 2)}"

    return answer


def get_history():
    stats = BotDB.get_history()
    answer = f"<b>DEPARTURE HISTORY</b> \n\n"
    for s in stats:
        if s[1] == 0:
            answer += "❌    "
        elif s[1] == 1:
            answer += "🟠    "
        else:
            answer += "✅    "
        answer += f"<i>{s[2]}</i> \n"

    return answer


def remove_last_entry():
    BotDB.remove_last_entry()
    return "LAST ENTRY REMOVED ✏️"


async def requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = update.message.text
    if value in {"❌", "🟠", "✅"}:
        answer = add_departure(value)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=answer,
                                       parse_mode=constants.ParseMode.HTML)
    elif value == "📊":
        answer = get_stats()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=answer,
                                       parse_mode=constants.ParseMode.HTML)
    elif value == "📖":
        answer = get_history()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=answer,
                                       parse_mode=constants.ParseMode.HTML)
    elif value == "✏️":
        answer = remove_last_entry()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=answer,
                                       parse_mode=constants.ParseMode.HTML)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='❌ Departure not added')


if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    start_handler = CommandHandler('start', start)
    requests_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), requests)

    application.add_handler(start_handler)
    application.add_handler(requests_handler)

    application.run_polling()
