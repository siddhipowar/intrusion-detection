# import cv2
# import numpy as np

# # Global variables
# draw = False  # True if the mouse is pressed
# rect = (0, 0, 0, 0)  # Coordinates of the rectangle
# start_point = (0, 0)  # Starting point of the rectangle
# frame1 = None  # Frame where the rectangle is drawn

# # Mouse callback function
# def click_event(event, x, y, flags, param):
#     global start_point, draw, frame1, rect

#     if event == cv2.EVENT_LBUTTONDOWN:
#         start_point = (x, y)
#         draw = True

#     elif event == cv2.EVENT_MOUSEMOVE:
#         if draw:
#             frame_copy = frame1.copy()
#             cv2.rectangle(frame_copy, start_point, (x, y), (0, 255, 0), 1)
#             cv2.imshow("frame", frame_copy)

#     elif event == cv2.EVENT_LBUTTONUP:
#         draw = False
#         rect = (start_point[0], start_point[1], x, y)
#         cv2.rectangle(frame1, start_point, (x, y), (0, 0, 255), 1)
#         cv2.imshow("frame", frame1)

# # Initialize video capture for the laptop camera
# cap = cv2.VideoCapture(0)

# # Check if the camera is opened correctly
# if not cap.isOpened():
#     raise IOError("Cannot open camera")

# # Set the camera resolution
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# # Read the first frame
# ret, frame1 = cap.read()
# if not ret:
#     print("Failed to grab the first frame.")
#     exit()

# frame1 = cv2.blur(frame1, (5, 5))  # Blur the frame to reduce noise

# # Display the first frame and set the mouse callback function
# cv2.imshow("frame", frame1)
# cv2.setMouseCallback("frame", click_event)

# # Wait until the user selects a region and presses a key
# cv2.waitKey(0)

# # Main loop for video processing
# while True:
#     ret, frame2 = cap.read()
#     if not ret:
#         break

#     # Pre-processing the frame
#     frame2 = cv2.blur(frame2, (5, 5))
#     diff = cv2.absdiff(frame1, frame2)
#     gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
#     _, thresh = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY)
#     dilated = cv2.dilate(thresh, None, iterations=3)

#     # Crop the area selected by the user
#     x, y, w, h = rect
#     crop = dilated[y:h, x:w]

#     # Find contours in the cropped region
#     contours, _ = cv2.findContours(crop, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

#     # Loop over contours to find if any large enough changes occurred
#     for contour in contours:
#         (x, y, w, h) = cv2.boundingRect(contour)

#         if cv2.contourArea(contour) < 900:
#             continue  # Ignore small changes

#         cv2.rectangle(frame1, (rect[0] + x, rect[1] + y), (rect[0] + x + w, rect[1] + y + h), (0, 0, 255), 2)
#         cv2.putText(frame1, "Intruder Found!", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

#     cv2.imshow('feed', frame1)
#     frame1 = frame2

#     if cv2.waitKey(40) == 27:  # Exit if ESC is pressed
#         break

# # Release the video capture and destroy all windows
# cap.release()
# cv2.destroyAllWindows()


import cv2
import numpy as np
import chronoptics.tof as tof

# Initialize 3D camera
# serial="2030019"
cam = tof.KeaCamera(serial="2030019")
tof.selectStreams(cam, [tof.FrameType.Z])
cam.start()

# Global variables for the intrusion detection system
draw = False  # True if the mouse is pressed. Used for selecting ROI.
roi_selected = False  # Flag to check if ROI has been selected
rect = (0, 0, 0, 0)  # Coordinates of the rectangle (ROI)
start_point = (0, 0)  # Starting point of the rectangle
DEPTH_THRESHOLD = (1000, 3000)  # depth threshold in mm

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
        # intrusion check in the specified ROI and depth range
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
