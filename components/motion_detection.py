import cv2
import numpy as np
import sys
from datetime import datetime

def setup_camera(camera_index=0):
    """Initialize the camera and video writer"""
    cap = cv2.VideoCapture(camera_index)

    # Check if camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera")
        sys.exit()

    # Get the actual frame size from the camera
    ret, test_frame = cap.read()
    if not ret:
        print("Error: Could not read from camera")
        sys.exit()

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Setup video writer with actual frame dimensions
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f'motion_detected_{timestamp}.avi'
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_filename, fourcc, 20.0, (frame_width, frame_height))

    return cap, out

def detect_motion(frame, last_frame, threshold=30):
    """Detect motion in frame using frame difference"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_diff = cv2.absdiff(last_frame, gray)
    _, thresh = cv2.threshold(frame_diff, threshold, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Find the largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        (x, y, w, h) = cv2.boundingRect(largest_contour)
        return True, (x, y, w, h)
    return False, (0, 0, 0, 0)

def main():
    # Initialize variables
    last_frame = None
    detected_motion = False
    frame_rec_count = 0
    MAX_FRAMES = 240  # 12 seconds at 20 fps

    try:
        # Setup camera and video writer
        cap, out = setup_camera()

        while True:
            # Read frame
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break

            # Convert frame to grayscale for motion detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Skip the first frame for stable motion detection
            if last_frame is None:
                last_frame = gray
                continue

            # Detect motion
            motion_detected, bbox = detect_motion(frame, last_frame)
            last_frame = gray

            # Draw rectangle if motion is detected
            if motion_detected:
                (x, y, w, h) = bbox
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                if not detected_motion:
                    print("Motion detected! Started recording.")
                    detected_motion = True

            # Show frame
            cv2.imshow('Motion Detection', frame)

            # Record frame if motion was detected
            if detected_motion:
                out.write(frame)
                frame_rec_count += 1

            # Exit conditions
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("User requested exit")
                break
            if frame_rec_count >= MAX_FRAMES:
                print("Maximum recording length reached")
                break

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        # Clean up
        if 'cap' in locals():
            cap.release()
        if 'out' in locals():
            out.release()
        cv2.destroyAllWindows()
        print("Cleanup completed")

if __name__ == "__main__":
    main()