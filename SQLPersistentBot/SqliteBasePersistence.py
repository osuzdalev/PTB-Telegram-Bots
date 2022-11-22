import sqlite3
from pprint import pformat

from telegram.ext import BasePersistence


class SqliteBasePersistence(BasePersistence):
    def __init__(self):
        self.conn = None
        self.cursor = None
        super().__init__()

    def connect_database(self, file_path):
        self.conn = sqlite3.connect(file_path)
        self.cursor = self.conn.cursor()

    async def get_bot_data(self):
        return {}

    async def update_bot_data(self, data):
        pass

    async def refresh_bot_data(self, bot_data):
        pass

    async def get_chat_data(self):
        return {}

    async def update_chat_data(self, chat_id, data):
        pass

    async def refresh_chat_data(self, chat_id, chat_data):
        pass

    async def drop_chat_data(self, chat_id):
        pass

    async def get_user_data(self):
        result = self.cursor.execute("SELECT * FROM `Main_Table` ORDER BY `user_id` DESC")
        print("get_user_data(): ", result.fetchall())

        self.cursor.execute("SELECT * FROM `Main_Table` ORDER BY `user_id` DESC")
        user_data = {}

        for row in self.cursor:
            if row[1] in user_data:
                user_data[row[1]][row[2]] = row[3]
            else:
                user_data[row[1]] = {row[2]: row[3]}

        print("user_data:\n{}".format(pformat(user_data)))

        return user_data

    async def fetch_user_data(self, key):
        result = self.cursor.execute("SELECT key_uuid FROM Main_Table WHERE key_uuid = (?)", (key,))
        return result.fetchall()[0][0]

    async def update_user_data(self, user_id, data):
        self.cursor.execute("INSERT INTO Main_Table(user_id, key_uuid, data) VALUES (?, ?, ?)",
                            (user_id, data[0], data[1]))
        self.conn.commit()

    async def refresh_user_data(self, user_id, user_data):
        pass

    async def remove_last(self, user_id):
        self.cursor.execute("DELETE FROM Main_Table WHERE (user_id = (?) AND ID = (SELECT MAX(id) FROM Main_Table))",
                            (user_id,))
        self.conn.commit()

    async def drop_user_data(self, user_id):
        self.cursor.execute("DELETE FROM Main_Table WHERE user_id = (?)",
                            (user_id,))
        self.conn.commit()

    async def get_callback_data(self):
        pass

    async def update_callback_data(self, data):
        pass

    async def get_conversations(self, name):
        pass

    async def update_conversation(self, name, key, new_state):
        pass

    async def flush(self):
        pass