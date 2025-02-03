import keyboard, time


def on_exam_start():
    def log(keycode):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open("eventlog.txt", "a") as f:
            f.write(f"{timestamp}:{keycode} pressed")
        
    keyboard.add_hotkey('ctrl+c', lambda: log('CTRL + C'), suppress=True)
    keyboard.add_hotkey('ctrl+v', lambda: log('CTRL + V'), suppress=True)
    
    while not end():
        time.sleep(1)
          
def end():
    pass

