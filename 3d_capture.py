import cv2
import numpy as np
import chronoptics.tof as tof

# Initialize 3D camera
serial="2030019"
cam = tof.KeaCamera(serial=serial)
tof.selectStreams(cam, [tof.FrameType.Z])
cam.start()

frames = cam.getFrames()
depth_frame = np.asarray(frames[0])
print(depth_frame.shape)


# Global variables for the intrusion detection system
draw = False  # True if the mouse is pressed. Used for selecting ROI.
roi_selected = False  # Flag to check if ROI has been selected
rect = (0, 0, 0, 0)  # Coordinates of the rectangle (ROI)
start_point = (0, 0)  # Starting point of the rectangle
DEPTH_THRESHOLD = (200, 500)  # depth threshold in mm
MIN_SIZE_THRESHOLD = 50  # Minimum number of pixels to consider as intrusion
TEMPORAL_THRESHOLD = 3  # Number of consecutive frames to confirm intrusion

# Variable for depicting sum of intrusions in consecutive frames
consecutive_intrusions = 0

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
def check_intrusion(depth_frame, rect, depth_threshold, min_size_threshold):
    # Crop the depth frame to the selected ROI
    x, y, x2, y2 = rect
    cropped_depth = depth_frame[y:y2, x:x2]
    
    intrusion_mask = (cropped_depth > depth_threshold[0]) & (cropped_depth < depth_threshold[1])
    intrusion_size = np.sum(intrusion_mask)

    intrusion_detected = intrusion_size > min_size_threshold
    return intrusion_detected, intrusion_size

cv2.namedWindow("Frame")
cv2.setMouseCallback("Frame", click_event)

while cam.isStreaming():
    frames = cam.getFrames()
    depth_frame = np.asarray(frames[0], dtype=np.float32)

    # depth converted to a visual format for display
    depth_visual = cv2.normalize(depth_frame, None, 0, 255, cv2.NORM_MINMAX)
    depth_visual = depth_visual.astype(np.uint8)  # Ensure the image is in 8-bit format

    # Color map applied to the normalized depth image
    colored_depth = cv2.applyColorMap(depth_visual, cv2.COLORMAP_JET)

    # Colored depth image for visualization and further processing
    frame = colored_depth

    if roi_selected:
        intrusion_detected, intrusion_size = check_intrusion(depth_frame, rect, DEPTH_THRESHOLD, MIN_SIZE_THRESHOLD)

        if intrusion_detected:
            consecutive_intrusions += 1
        else:
            consecutive_intrusions = 0

        if consecutive_intrusions >= TEMPORAL_THRESHOLD:
            # If intrusion is observed in frames equal to or more than temporal threshold defined, then display the text as intrusion detected
            cv2.putText(frame, "Intrusion Detected!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            consecutive_intrusions = 0 # Reset after alarming
        
        
        cv2.rectangle(frame, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 0), 2)

    cv2.imshow("Frame", frame)

    # Break the loop with the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cam.stop()
cam = None
cv2.destroyAllWindows()


