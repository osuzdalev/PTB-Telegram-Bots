import sqlite3


class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def add_departure(self, departure_type):
        self.cursor.execute("INSERT INTO Departure_Table(departure_type) VALUES (?)", (departure_type,))
        self.conn.commit()

    def get_departure_stats(self):
        result = self.cursor.execute("SELECT departure_type FROM Departure_Table")
        return result.fetchall()

    def get_history(self):
        result = self.cursor.execute("SELECT * FROM `Departure_Table` ORDER BY `date`")
        return result.fetchall()

    def remove_last_entry(self):
        self.cursor.execute("DELETE FROM Departure_Table WHERE ID = (SELECT MAX(id) FROM Departure_Table)")
        self.conn.commit()

    def close(self):
        self.conn.close()
