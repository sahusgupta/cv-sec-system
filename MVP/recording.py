import pyautogui as pag
import cv2
import numpy as np
import ctypes

user32 = ctypes.windll.user32
width = user32.GetSystemMetrics(0)
height = user32.GetSystemMetrics(1)

resolution = (width, height)
codec = cv2.VideoWriter.fourcc(*"mp4v")
filename = "Out.mp4"
fps = 30.0
out = cv2.VideoWriter(filename, codec, fps, resolution)
cv2.namedWindow("Monitoring", cv2.WINDOW_FREERATIO)

while True:
    img = np.array(pag.screenshot())
    frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    out.write(frame)
    cv2.imshow("Monitoring", frame)
    
    if cv2.waitKey(1) == ord('q'):
        break

out.release()
cv2.destroyAllWindows()