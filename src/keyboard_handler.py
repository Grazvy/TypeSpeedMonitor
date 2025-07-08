import time
from pynput import keyboard

from src.db_handlers import DBWriter

MIN_BIN_SIZE = 5
RECORDING_THRESHOLD = 1.0

class KeyboardHandler:
    def __init__(self):
        self.db = DBWriter()
        self.listener = None
        self.last_key_press = time.time()
        self.current_bin = []

    def start_monitoring(self):
        self.listener = keyboard.Listener(on_press=lambda key: self.on_press(key))
        self.listener.start()

    def on_press(self, key):
        # only monitor characters
        if not hasattr(key, 'char') or key.char is None:
            return

        current_time = time.time()
        time_passed = current_time - self.last_key_press

        if self.last_key_press // MIN_BIN_SIZE < current_time // MIN_BIN_SIZE:
            self.load_current_bin()

        if time_passed < RECORDING_THRESHOLD:
            self.current_bin.append(time_passed)

        self.last_key_press = current_time

    def load_current_bin(self):
        if self.current_bin:
            mean = sum(self.current_bin) / len(self.current_bin)
            self.db.insert_data(self.last_key_press, round(60 / (mean * 5)))
            print("loaded ", mean)
            self.current_bin = []

    def stop(self):
        if self.listener:
            print("Stopping listener...")
            self.listener.stop()

        self.listener.join()
        self.db.close()