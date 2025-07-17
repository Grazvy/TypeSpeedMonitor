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


def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_config_path():
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            # For config files, we want to use a persistent location
            app_name = "TypeSpeedMonitor"
            user_dir = user_data_dir(app_name)
            os.makedirs(user_dir, exist_ok=True)
        else:
            # Other executable builders
            user_dir = os.path.dirname(sys.executable)
    else:
        # Running in development environment
        user_dir = os.path.dirname(os.path.abspath(__file__))

    config_path = os.path.join(user_dir, 'config.json')

    # Create default config if it doesn't exist
    if not os.path.exists(config_path):
        create_default_config(config_path)

    return config_path


def check_input_monitoring_trusted():   # also possible using keyboard_handler?
    import Quartz
    def _dummy_callback(proxy, type_, event, refcon):
        return event

    event_mask = Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown)

    tap = Quartz.CGEventTapCreate(
        Quartz.kCGSessionEventTap,  # Tap at the session level
        Quartz.kCGHeadInsertEventTap,  # Insert at head to test priority
        0,  # Active (not listen-only)
        event_mask,
        _dummy_callback,
        None
    )

    if not tap:
        return False

    runLoopSource = Quartz.CFMachPortCreateRunLoopSource(None, tap, 0)
    if not runLoopSource:
        return False

    return True


def create_default_config(config_path):
    default_config = {
        "dark_mode": False,
        "mult": 15,
        "summary_of": "day"
    }

    try:
        import json
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=4)
        print(f"Created default config at: {config_path}")
    except Exception as e:
        print(f"Error creating default config: {e}")


def load_config():
    path = get_config_path()
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
