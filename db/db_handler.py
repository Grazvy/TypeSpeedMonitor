import os
import sqlite3
from appdirs import user_data_dir


class DBHandler:
    def __init__(self):
        self.data_dir = user_data_dir("TypeSpeedMonitor")
        os.makedirs(self.data_dir, exist_ok=True)
        db_path = os.path.join(self.data_dir, "data.db")
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS log_data (timestamp INTEGER PRIMARY KEY, value INTEGER)")

    def insert_data(self, timestamp, value):
        self.cur.execute(
            "INSERT OR IGNORE INTO log_data (timestamp, value) VALUES (?, ?)",
            (timestamp, value)
        )
        self.conn.commit()

    def get_data(self, start, end):
        self.cur.execute(
            "SELECT * FROM log_data WHERE timestamp BETWEEN ? AND ?",
            (start, end)
        )
        return self.cur.fetchall()

    def close(self):
        self.conn.close()
