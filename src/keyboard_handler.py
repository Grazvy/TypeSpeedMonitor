import time

from src.db_handlers import DBWriter

RECORDING_THRESHOLD = 1.0
MIN_RECORDINGS = 8
EXCLUDED_KEYS = {}

EXCEPTIONS = {
    '(', ')', '[', ']', '{', '}', '<', '>',
    ':', ';', ',', '.', '?', '!',
    '+', '-', '*', '/', '%', '=',
    '&', '|', '^', '~', '!',
    '@', '#', '$', '\\', '_', '`', '"', "'",
}

class KeyboardHandler:
    def __init__(self, min_bin_size):
        self.db = DBWriter()
        self.listener = None
        self.last_key_press = time.time()
        self.min_bin_size = min_bin_size
        self.current_bin = []
        self.excluded_keys_pressed = set()

    def start_monitoring(self):
        from pynput import keyboard
        global EXCLUDED_KEYS
        EXCLUDED_KEYS = {
            keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r,
            keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r,
            keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r,
            keyboard.Key.tab, keyboard.Key.enter, keyboard.Key.esc,
            keyboard.Key.backspace, keyboard.Key.delete,
            keyboard.Key.up, keyboard.Key.down, keyboard.Key.left, keyboard.Key.right,
            keyboard.Key.home, keyboard.Key.end, keyboard.Key.page_up, keyboard.Key.page_down
        }
        #self.listener = keyboard.Listener(on_press=lambda key: self.on_press(key))
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def on_press(self, key):
        # ignore special keys
        if key in EXCLUDED_KEYS:
            self.excluded_keys_pressed.add(key)
            return

        # ignore non-characters
        if not hasattr(key, 'char'):
            return

        if self.excluded_keys_pressed and key.char not in EXCEPTIONS:
            return

        current_time = time.time()
        time_passed = current_time - self.last_key_press

        if self.last_key_press // self.min_bin_size < current_time // self.min_bin_size:
            self.process_current_bin()

        if time_passed < RECORDING_THRESHOLD:
            self.current_bin.append(time_passed)

        self.last_key_press = current_time

    def on_release(self, key):
        # Remove from pressed keys set if released
        if key in self.excluded_keys_pressed:
            self.excluded_keys_pressed.discard(key)

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
