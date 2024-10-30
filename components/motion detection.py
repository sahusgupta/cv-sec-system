import cv2
import numpy as np
import sys
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from object_detector import NaiveBayes
from sklearn.preprocessing import LabelEncoder
from PIL import Image
is_person = NaiveBayes()
is_person.train()
image_data = [np.array(Image.open('../WIN_20241030_11_42_34_Pro.jpg').resize((64, 64))).flatten().tolist()]
is_person_prediction = is_person.predict(image_data)[0]
print("person" if is_person_prediction >= 0.5 else "object")
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

def plot_contours(plot, frame, contours):
    """Plot the contours on a Matplotlib plot"""
    plot.clear()
    plot.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    plot.set_title('Motion Detection')

    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        plot.add_patch(plt.Rectangle((x, y), w, h, fill=False, color='green', linewidth=2))

    plt.axis('off')
    plt.draw()
    plt.pause(0.001)
def process_image(frame, bbox):
    (x, y, w, h) = bbox
    roi = frame[y:y+h, x:x+w]
    roi = cv2.resize(roi, (64, 64))
    image_data = [np.array(roi).flatten().tolist()]
    is_person_prediction = is_person.predict(image_data)[0]
    if is_person_prediction == 'person':
        return (0, 0, 0)
        cv2.imwrite(f'person_detected_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg', roi)
    else:
        return (0, 0, 255)
def main():
    last_frame = None
    detected_motion = False
    frame_rec_count = 0
    MAX_FRAMES = 240
    fig, ax = plt.subplots(figsize=(8, 6))
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
                color = process_image(frame, bbox)
                plot_contours(ax, frame, contours)                
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                if not detected_motion:
                    print("Motion detected! Started recording.")
                    detected_motion = True
                plot_contours(ax, frame, contours)

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