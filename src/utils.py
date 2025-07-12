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
    fig.patch.set_facecolor("#222222")
    ax.set_facecolor("#222222")
    ax.tick_params(colors="white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.title.set_color("white")

    for spine in ax.spines.values():
        spine.set_color("white")

def apply_light_theme(ax):
    fig = ax.figure
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")
    ax.tick_params(colors="black")
    ax.xaxis.label.set_color("black")
    ax.yaxis.label.set_color("black")
    ax.title.set_color("black")

    for spine in ax.spines.values():
        spine.set_color("black")
