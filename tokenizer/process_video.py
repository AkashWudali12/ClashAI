import cv2
import numpy as np

def get_state_from_frame(frame):
    """return state object from frame in video"""
    pass

def analyze_video_frame_by_frame(video_path, template_path):

    template = cv2.imread(template_path, 0) # Read in grayscale for simplicity/speed
    if template is None:
        print(f"Error: Could not load template image at {template_path}")
        return

    # Get the width and height of the template
    w, h = template.shape[::-1] 
    
    # Define the template matching method
    # Normalized Cross-Correlation is robust and works well
    method = cv2.TM_CCOEFF_NORMED


    # 1. Open the video file
    # 0 is often used for the default camera, but for a file, use the path.
    cap = cv2.VideoCapture(video_path)

    # Check if video opened successfully
    if not cap.isOpened():
        print(f"Error: Could not open video file at {video_path}")
        return

    # A counter to track which frame we are processing
    frame_count = 0

    print("--- Starting Frame-by-Frame Analysis ---")

    # 2. Loop through the frames
    while cap.isOpened():
        # Read the next frame
        # 'ret' (boolean) is True if a frame was successfully read, False otherwise
        # 'frame' is the actual frame (a numpy array)
        ret, frame = cap.read()

        if ret:
            # --- START: Template Matching Logic ---

            # Convert the current frame to grayscale
            # Matching in grayscale often gives better results and is faster
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Perform Template Matching
            # The result is a 2D array (result_matrix) where each element 
            # represents the match score at that (x, y) location.
            result_matrix = cv2.matchTemplate(gray_frame, template, method)
            
            # Find the best match location
            # minVal: minimum score, maxVal: maximum score
            # minLoc: location (x, y) of the minimum score, maxLoc: location of the maximum score
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_matrix)
            
            # For TM_CCOEFF_NORMED, the best match is the maximum value
            top_left = max_loc
            
            # Define the coordinates for the bounding box
            bottom_right = (top_left[0] + w, top_left[1] + h)
            
            # You can set a threshold to ignore bad matches
            threshold = 0.3 # A score close to 1.0 is a perfect match
            print(max_loc, max_val)
            if max_val >= threshold:
                # Draw the bounding box on the original color frame
                cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2) # Green box, thickness 2
                
                # Optional: Add text showing the confidence score
                cv2.putText(frame, f"Match: {max_val:.2f}", (top_left[0], top_left[1] - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            # --- END: Template Matching Logic ---

            # Display the result
            cv2.imshow('Video with Bounding Box', frame)
            
            # Exit on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            # Break the loop if 'ret' is False (i.e., we've reached the end of the video)
            print("\nEnd of video stream.")
            break

    # 3. Release the video object and destroy all windows
    cap.release()
    cv2.destroyAllWindows()
    print("--- Analysis Complete ---")

def run_background_extraction(video_path):
    # Use Mixture of Gaussain distribution models
    # basically colors (rgb vals) that appear in many consecutive frames will be considered part of the background
    # backSub = cv2.createBackgroundSubtractorMOG2(history=10, varThreshold=50, detectShadows=True)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    backSub = cv2.bgsegm.createBackgroundSubtractorGMG(initializationFrames=120, decisionThreshold=0.8)

    cap = cv2.VideoCapture(video_path)

    # Check if video opened successfully
    if not cap.isOpened():
        print(f"Error: Could not open video file at {video_path}")
        return

    print("--- Starting Frame-by-Frame Analysis ---")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # --- THE CORE LOGIC ---
        # Apply the subtractor to get the foreground mask
        fg_mask = backSub.apply(frame)

        # Clean up the mask (Morphological Operations)
        # kernel = np.ones((5, 5), np.uint8)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.dilate(fg_mask, kernel, iterations=2)

        # Find and draw contours on the ORIGINAL frame
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            if cv2.contourArea(cnt) > 200: # Adjust based on character size
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, "Moving Object", (x, y-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # --- LOCAL DISPLAY ---
        cv2.imshow('Clash Detector - Result', frame)
        # cv2.imshow('MOG2 Background Mask', fg_mask)

        # Press 'q' to exit the loop
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


video_file_path = 'videos/vid_2.mp4' 
template_image_path = "images/default_arena.jpeg"
run_background_extraction(video_file_path)