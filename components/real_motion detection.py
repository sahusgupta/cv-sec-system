import cv2
import numpy as np
import sys
from datetime import datetime

def cam(cam_index=0):
    capture_device = cv2.VideoCapture(cam_index)

    if not capture_device.isOpened():
        sys.exit()
    frame_width = int(capture_device.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(capture_device.get(cv2.CAP_PROP_FRAME_HEIGHT))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    return capture_device

def motion(frame, last_frame, threshold=60):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_difference = cv2.absdiff(last_frame, gray)
    _, thresh = cv2.threshold(frame_difference, threshold, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        (x,y,w,h) = cv2.boundingRect(largest_contour)
        return True, (x, y, w, h)
    return False, (0, 0, 0, 0)

def main():

    last = None
    detected = False
    frames_recorded_count = 0

    try:

        cap = cam()

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Couldn't parse frame")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if last is None:
                last = gray
                continue
            
            motion_detected, bbox = motion(frame, last)
            last = gray

            if motion_detected:
                (x, y, w, h) = bbox
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print('User exit')
                break
    except Exception as e:
        print(f"an error occurred: {str(e)}")
    
    finally:
        if "cap" in locals():
            cap.release()
        
        cv2.destroyAllWindows()
        print('cleaned')


if __name__ == "__main__":
    main()

