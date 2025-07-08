import os
import sqlite3
from appdirs import user_data_dir


def get_db_path():
    data_dir = user_data_dir("TypeSpeedMonitor")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "data.db")


def init_database():
    db_path = get_db_path()

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS log_data (timestamp INTEGER PRIMARY KEY, value INTEGER)")
    conn.commit()
    conn.close()
