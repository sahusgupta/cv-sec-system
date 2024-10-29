import cv2
import numpy as np
import sys
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def setup_camera(camera_index=0):
    """Initialize the camera and video writer"""
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print("Error: Could not open camera")
        sys.exit()

    ret, test_frame = cap.read()
    if not ret:
        print("Error: Could not read from camera")
        sys.exit()

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    return cap, None

def detect_motion(frame, last_frame, threshold=30):
    """Detect motion in frame using frame difference"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_diff = cv2.absdiff(last_frame, gray)
    _, thresh = cv2.threshold(frame_diff, threshold, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        (x, y, w, h) = cv2.boundingRect(largest_contour)
        return True, (x, y, w, h), contours
    return False, (0, 0, 0, 0), []

def plot_contours(frame, contours):
    """Plot the contours on a Matplotlib plot"""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    ax.set_title('Motion Detection')

    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        ax.add_patch(plt.Rectangle((x, y), w, h, fill=False, color='green', linewidth=2))

    plt.axis('off')
    plt.draw()
    plt.pause(0.001)

def main():
    last_frame = None
    detected_motion = False
    frame_rec_count = 0
    MAX_FRAMES = 240

    try:
        cap, out = setup_camera()

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if last_frame is None:
                last_frame = gray
                continue

            motion_detected, bbox, contours = detect_motion(frame, last_frame)
            last_frame = gray

            if motion_detected:
                (x, y, w, h) = bbox
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                if not detected_motion:
                    print("Motion detected! Started recording.")
                    detected_motion = True
                plot_contours(frame, contours)

            cv2.imshow('Motion Detection', frame)

            # Exit conditions
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("User requested exit")
                plt.savefig('motion_detection.png')
                break

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        # Clean up
        if 'cap' in locals():
            cap.release()
        cv2.destroyAllWindows()
        print("Cleanup completed")

if __name__ == "__main__":
    main()