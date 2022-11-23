from configparser import ConfigParser
import logging

from telethon.sync import TelegramClient, events

logger_test_client_request = logging.getLogger(__name__)

CONSTANTS = ConfigParser()
CONSTANTS.read("../constants.ini")

api_id = int(CONSTANTS.get("API", "ID"))
api_hash = CONSTANTS.get("API", "HASH")
token = CONSTANTS.get("ORDER_DISPATCHER_BOT", "TOKEN")
chat_id = CONSTANTS.get("TELEGRAM_ID", "USER_ID_MAIN")


if __name__ == "__main__":
    with TelegramClient('name', api_id, api_hash) as client:
        client.send_message('me', 'Hello, myself!')
        # print(client.download_profile_photo('me'))

        @client.on(events.NewMessage(pattern='(?i).*Hello'))
        async def handler(event):
            await event.reply('Hey!')

        client.run_until_disconnected()
