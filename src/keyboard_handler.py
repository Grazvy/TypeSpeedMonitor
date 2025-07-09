import time
from pynput import keyboard

from src.db_handlers import DBWriter

RECORDING_THRESHOLD = 1.0
MIN_RECORDINGS = 8

class KeyboardHandler:
    def __init__(self, min_bin_size):
        self.db = DBWriter()
        self.listener = None
        self.last_key_press = time.time()
        self.min_bin_size = min_bin_size
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

        if self.last_key_press // self.min_bin_size < current_time // self.min_bin_size:
            self.process_current_bin()

        if time_passed < RECORDING_THRESHOLD:
            self.current_bin.append(time_passed)

        self.last_key_press = current_time

    def process_current_bin(self):
        if len(self.current_bin) < MIN_RECORDINGS:
            self.current_bin = []
        else:
            mean = sum(self.current_bin) / len(self.current_bin)
            wpm = round(60 / (mean * 5))
            self.db.insert_data(int(self.last_key_press), wpm)
            print("loaded", wpm, "WMP")
            self.current_bin = []

    def stop(self):
        if self.listener:
            print("Stopping listener...")
            self.listener.stop()

        self.listener.join()
        self.db.close()
