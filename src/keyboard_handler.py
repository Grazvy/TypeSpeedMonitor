from pynput import keyboard

class KeyboardHandler:
    def __init__(self, db):
        self.db = db
        self.listener = None

    def start_monitoring(self):
        self.listener = keyboard.Listener(on_press=lambda key: self.on_press(key))
        self.listener.start()

    def on_press(self, key):
        pass

    def stop(self):
        if self.listener:
            print("Stopping listener...")
            self.listener.stop()