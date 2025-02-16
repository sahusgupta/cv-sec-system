import pyautogui as pag
import cv2
import numpy as np
import ctypes
import time
import keyboard
import screeninfo
import pyperclip
import threading
from process import process_frames

class ExamMonitor:
    def __init__(self):
        self.last_clipboard_content = pyperclip.paste()
        self.monitoring = False
        self.log_file = "eventlog.txt"
        self.screenshot_interval = 60  # Screenshot every 60 seconds
        self.last_screenshot_time = 0
        
        # Clear the log file on startup
        with open(self.log_file, "w") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: === New Session Started ===\n")
    
    def log(self, event):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"{timestamp}: {event}\n")

    def clipboard_monitor(self):
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
    def one_display(self):
        return len(screeninfo.get_monitors()) == 2

    def take_screenshot(self):
        current_time = time.time()
        if current_time - self.last_screenshot_time >= self.screenshot_interval:
            screenshot = pag.screenshot()
            screenshot_filename = f"screenshot_{time.strftime('%Y%m%d_%H%M%S')}.png"
            screenshot.save(screenshot_filename)
            self.log(f"SCREENSHOT_TAKEN: {screenshot_filename}")
            self.last_screenshot_time = current_time

    def start_monitoring(self):
        if not self.one_display():
            self.log("MULTIPLE_DISPLAYS_DETECTED")
            return False
        self.monitoring = True
        self.clipboard_thread = threading.Thread(target=self.clipboard_monitor)
        self.clipboard_thread.start()

        # Set up hotkey logging with clipboard tracking
        keyboard.add_hotkey('ctrl+c', lambda: self.log('CTRL + C'), suppress=True)
        keyboard.add_hotkey('ctrl+v', lambda: self.log('CTRL + V'), suppress=True)
        keyboard.add_hotkey('ctrl+n', lambda: self.log('CTRL + N'), suppress=True)

        return True
    
    def stop_monitoring(self):
        self.monitoring = False
        if hasattr(self, 'clipboard_thread'):
            self.clipboard_thread.join()
        keyboard.unhook_all()
        
def main():
    user32 = ctypes.windll.user32
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)

    webcam = cv2.VideoCapture(0) 
    webcam_width = int(webcam.get(cv2.CAP_PROP_FRAME_WIDTH))
    webcam_height = int(webcam.get(cv2.CAP_PROP_FRAME_HEIGHT))

    overlay_width = webcam_width // 5
    overlay_height = webcam_height // 5

    # Video writer setup
    resolution = (width, height)
    codec = cv2.VideoWriter.fourcc(*"mp4v")
    filename = "exam_recording.mp4"
    fps = 30.0
    out = cv2.VideoWriter(filename, codec, fps, resolution)

    monitor = ExamMonitor()
    frame_count = 0
    last_process_time = time.time()
    frame_buffer = []
    
    try:
        if monitor.start_monitoring():
            print("Exam monitoring started. Press Ctrl+Alt+Q to quit.")
            
            while True:
                monitor.take_screenshot()
                frame_count += 1

                img = np.array(pag.screenshot())
                frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                ret, webcam_frame = webcam.read()
                if ret:
                    webcam_frame = cv2.resize(webcam_frame, (overlay_width, overlay_height))
                    
                    y_offset = 10  # pixels from top
                    x_offset = width - overlay_width - 10  # pixels from right
                    
                    frame[y_offset:y_offset+overlay_height, 
                          x_offset:x_offset+overlay_width] = webcam_frame
                
                out.write(frame)

                if frame_count % 60 == 0:
                    frame_filename = f"frame_{time.strftime('%Y%m%d_%H%M%S')}.png"
                    cv2.imwrite(frame_filename, frame)
                    frame_buffer.append(frame_filename)

                current_time = time.time()
                if current_time - last_process_time >= 1.0 and frame_buffer:
                    criteria = ["looking away from screen", "multiple people present", "phone visible", "suspicious objects", 'constant looking down', 'mouth moving', 'wearing headphones']
                    result = process_frames(frame_buffer, criteria)
                    
                    
                    monitor.log(f"BEHAVIOR_ANALYZED: Score={result['overall_probability']}, Details={result['criteria_confidences']}")
                    
                    frame_buffer = []
                    last_process_time = current_time
                
                if keyboard.is_pressed('ctrl+alt+q'):
                    break
                
                time.sleep(0.1)  # Prevent high CPU usage

        else:
            print("Failed to start monitoring due to multiple displays.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Cleanup
        monitor.stop_monitoring()
        webcam.release()
        out.release()
        cv2.destroyAllWindows()
if __name__ == "__main__":
    main()