import cv2
import numpy as np
import chronoptics.tof as tof
from PIL import Image

# Initialize 3D camera
serial = "203001c"
cam = tof.KeaCamera(serial=serial)
tof.selectStreams(cam, [tof.FrameType.Z])
cam.start()

# Global variables for the intrusion detection system
draw = False  # True if the mouse is pressed. Used for selecting ROI.
roi_selected = False  # Flag to check if ROI has been selected
rect = (0, 0, 0, 0)  # Coordinates of the rectangle (ROI)
start_point = (0, 0)  # Starting point of the rectangle
DEPTH_THRESHOLD = (1000, 3000)  # Example depth threshold in mm

# Mouse callback function for selecting ROI
def click_event(event, x, y, flags, param):
    global start_point, draw, rect, roi_selected

    if event == cv2.EVENT_LBUTTONDOWN:
        start_point = (x, y)
        draw = True
        roi_selected = False

    elif event == cv2.EVENT_MOUSEMOVE and draw:
        end_point = (x, y)
        cv2.rectangle(frame, start_point, end_point, (0, 255, 0), 1)
        cv2.imshow("Frame", frame)

    elif event == cv2.EVENT_LBUTTONUP:
        draw = False
        roi_selected = True
        rect = (start_point[0], start_point[1], x, y)
        cv2.rectangle(frame, start_point, (x, y), (0, 255, 0), 2)
        cv2.imshow("Frame", frame)

# Function to check for intrusion in the selected ROI and depth range
def check_intrusion(depth_frame, rect, depth_threshold):
    # Crop the depth frame to the selected ROI
    x, y, x2, y2 = rect
    cropped_depth = depth_frame[y:y2, x:x2]
    
    # Check for presence within the depth threshold
    intrusion_detected = np.any((cropped_depth > depth_threshold[0]) & (cropped_depth < depth_threshold[1]))
    return intrusion_detected

cv2.namedWindow("Frame")
cv2.setMouseCallback("Frame", click_event)

while True:
    frames = cam.getFrames()
    depth_frame = np.asarray(frames[0], dtype=np.float32)

    # Convert depth to a visual format for display
    depth_visual = cv2.normalize(depth_frame, None, 0, 255, cv2.NORM_MINMAX)
    frame = cv2.cvtColor(depth_visual.astype(np.uint8), cv2.COLOR_GRAY2BGR)

    if roi_selected:
        # Check if there's an intrusion in the specified ROI and depth range
        if check_intrusion(depth_frame, rect, DEPTH_THRESHOLD):
            cv2.putText(frame, "Intrusion Detected!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.rectangle(frame, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 0), 2)

    cv2.imshow("Frame", frame)

    # Break the loop with the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cam.stop()
cv2.destroyAllWindows()
