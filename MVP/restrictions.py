import keyboard
import time
import screeninfo
import pyperclip
import threading
import pygetwindow as gw

class ExamMonitor:
    def __init__(self):
        self.last_clipboard_content = pyperclip.paste()
        self.monitoring = False
        self.log_file = "eventlog.txt"
        self.active_window = gw.getActiveWindow().title if gw.getActiveWindow() else "Unknown"

    def log(self, event):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"{timestamp}: {event}\n")

    def _clipboard_monitor(self):
        while self.monitoring:
            try:
                current_clipboard = pyperclip.paste()
                if current_clipboard != self.last_clipboard_content:
                    self.log(f"CLIPBOARD_CHANGE: {current_clipboard}")
                    self.last_clipboard_content = current_clipboard
                time.sleep(0.5)
            except Exception as e:
                self.log(f"CLIPBOARD_MONITOR_ERROR: {str(e)}")
                break

    def _focus_monitor(self):
        """
        Detects if the user changes focus (switches applications or tabs out).
        """
        while self.monitoring:
            current_window = gw.getActiveWindow().title if gw.getActiveWindow() else "Unknown"
            if current_window != self.active_window:
                self.log(f"Focus changed! User switched to: {current_window}")
                self.active_window = current_window
            time.sleep(1)

    def one_display(self):
        return len(screeninfo.get_monitors()) == 1

    def start_monitoring(self):
        if not self.one_display():
            self.log("MULTIPLE_DISPLAYS_DETECTED")
            return False

        self.monitoring = True
        self.clipboard_thread = threading.Thread(target=self._clipboard_monitor)
        self.focus_thread = threading.Thread(target=self._focus_monitor)  # New focus tracking thread
        self.clipboard_thread.start()
        self.focus_thread.start()

        keyboard.add_hotkey('ctrl+c', lambda: self.log('CTRL + C'), suppress=True)
        keyboard.add_hotkey('ctrl+v', lambda: self.log('CTRL + V'), suppress=True)
        keyboard.add_hotkey('ctrl+n', lambda: self.log('CTRL + N'), suppress=True)
        keyboard.add_hotkey('alt+tab', lambda: self.log('ALT + TAB'), suppress=True)
        return True

    def stop_monitoring(self):
        self.monitoring = False
        if hasattr(self, 'clipboard_thread'):
            self.clipboard_thread.join()
        if hasattr(self, 'focus_thread'):
            self.focus_thread.join()
        keyboard.unhook_all()
