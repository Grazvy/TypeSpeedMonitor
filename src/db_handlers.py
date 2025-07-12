import sqlite3
from src.utils import get_db_path


class DBWriter:
    def __init__(self):
        db_path = get_db_path()
        self.conn = sqlite3.connect(db_path, check_same_thread=False)

        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")

        self.cur = self.conn.cursor()

    def insert_data(self, timestamp, value):
        self.cur.execute(
            "INSERT OR IGNORE INTO log_data (timestamp, value) VALUES (?, ?)",
            (timestamp, value)
        )
        self.conn.commit()

    def close(self):
        print("Closing database writing connection...")
        self.conn.close()

class DBReader():
    def __init__(self):
        db_path = get_db_path()
        self.conn = sqlite3.connect(db_path, check_same_thread=False)

        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA query_only=1")

        self.cur = self.conn.cursor()

    def read_data(self, start, end):
        self.cur.execute(
            "SELECT * FROM log_data WHERE timestamp BETWEEN ? AND ?",
            (start, end)
        )
        return self.cur.fetchall()

    def get_max(self, point, distance):
        self.cur.execute("""
            SELECT MAX(value)
            FROM log_data
            WHERE timestamp BETWEEN ? AND ?
        """, (point - distance, point + distance))
        result = self.cur.fetchone()
        return result[0] if result and result[0] is not None else 60

    def close(self):
        print("Closing database reading connection...")
        self.conn.close()

