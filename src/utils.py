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


def apply_dark_theme(ax):
    fig = ax.figure
    fig.patch.set_facecolor("#082026")
    ax.set_facecolor("#0a3b3b")
    ax.tick_params(colors="#ECEFF4")
    ax.xaxis.label.set_color("#ECEFF4")
    ax.yaxis.label.set_color("#ECEFF4")
    ax.title.set_color("#ECEFF4")

    for spine in ax.spines.values():
        spine.set_color("#ECEFF4")

def apply_light_theme(ax):
    fig = ax.figure
    fig.patch.set_facecolor("#ECEFF4")
    ax.set_facecolor("#ECEFF4")
    ax.tick_params(colors="#3B4252")
    ax.xaxis.label.set_color("#3B4252")
    ax.yaxis.label.set_color("#3B4252")
    ax.title.set_color("#3B4252")

    for spine in ax.spines.values():
        spine.set_color("#3B4252")