import pyautogui as pag
import cv2  
import numpy as np
import ctypes

# Get screen dimensions
user32 = ctypes.windll.user32
width = user32.GetSystemMetrics(0)
height = user32.GetSystemMetrics(1)

# Initialize webcam
webcam = cv2.VideoCapture(0) 
webcam_width = int(webcam.get(cv2.CAP_PROP_FRAME_WIDTH))
webcam_height = int(webcam.get(cv2.CAP_PROP_FRAME_HEIGHT))

overlay_width = webcam_width // 5
overlay_height = webcam_height // 5

# Video writer setup
resolution = (width, height)
codec = cv2.VideoWriter.fourcc(*"mp4v")
filename = "Out.mp4"
fps = 30.0
out = cv2.VideoWriter(filename, codec, fps, resolution)
# cv2.namedWindow("Monitoring", cv2.WINDOW_FREERATIO)

while True:
    img = np.array(pag.screenshot())
    frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    ret, webcam_frame = webcam.read()
    if ret:
        webcam_frame = cv2.resize(webcam_frame, (overlay_width, overlay_height))
        
        y_offset = 10  #  pixels from top
        x_offset = width - overlay_width - 10  # pixels from right
        
        overlay_region = frame[y_offset:y_offset+overlay_height, 
                             x_offset:x_offset+overlay_width]
        
        frame[y_offset:y_offset+overlay_height, 
              x_offset:x_offset+overlay_width] = webcam_frame
    
    out.write(frame)
    # cv2.imshow("Monitoring", frame)
    
    if cv2.waitKey(1) == ord('q'):
        break

webcam.release()
out.release()
cv2.destroyAllWindows()