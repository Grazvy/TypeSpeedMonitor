import json
import os
import sqlite3
import sys

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


def get_config_path():
    # Use application directory whether run normally or with PyInstaller
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS  # PyInstaller temp directory
        user_dir = os.path.dirname(sys.executable)
    else:
        user_dir = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(user_dir, 'config.json')


def load_config():
    path = get_config_path()
    print(path)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    else:
        return {}  # default empty config


def save_config(config_dict):
    path = get_config_path()
    with open(path, 'w') as f:
        json.dump(config_dict, f, indent=4)


def apply_dark_theme(ax):
    fig = ax.figure
    fig.patch.set_facecolor((0.0, 0.0, 0.0, 0.0))
    ax.set_facecolor("#0a3b3b")
    ax.tick_params(colors="#ECEFF4")
    ax.xaxis.label.set_color("#ECEFF4")
    ax.yaxis.label.set_color("#ECEFF4")
    ax.title.set_color("#ECEFF4")

    for spine in ax.spines.values():
        spine.set_color("#ECEFF4")


def apply_light_theme(ax):
    fig = ax.figure
    fig.patch.set_facecolor((0.0, 0.0, 0.0, 0.0))
    ax.set_facecolor("#cbe7e3")
    ax.tick_params(colors="#3B4252")
    ax.xaxis.label.set_color("#3B4252")
    ax.yaxis.label.set_color("#3B4252")
    ax.title.set_color("#3B4252")

    for spine in ax.spines.values():
        spine.set_color("#3B4252")
