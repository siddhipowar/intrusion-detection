# intrusion-detection

An application that uses Gordon for intrusion detection within a specified region of interest (ROI) and depth range.

Algorithm:

* Initialize camera using it’s serial number and used Z frame type 
* Captured frames while camera is streaming 
* Converted those frames to arrays for processing
* Also converted frames to a visual format to display using OpenCV
* User can select a rectangular area in which intrusion will be detected while the camera is streaming in real-time
* Global variables used:
    ‘draw’ and ‘roi_selected’ are boolean flags that indicate whether mouse is currently being used to draw the ROI and whether an ROI has been selected
    ‘rect’ stores the coordinates of the drawn rectangle (ROI)
    ‘start_point’ holds the initial point where the mouse was clicked to start drawing the ROI
    ‘DEPTH_THRESHOLD’ defines the minimum and maximum depth range in millimeters for detecting intrusion

    ‘click_event’: It is a mouse callback function. This function updates global variables based on the mouse actions.
        - When left mouse button is pressed down, it starts the process of drawing the rectangle by recording the starting point
        - As the mouse moves with the button pressed, it dynamically updates the rectangle on the frame
        - When the left mouse button is released, it finalizes the ROI and updates the ‘rect’ with its coordinates
* Intrusion detection function (‘check_intrusion’):
    -  This function crops the depth frame based on the rectangle coordinates
    -   While camera is streaming, if any points in the cropped area fall within the specified depth threshold then an intrusion is indicated
