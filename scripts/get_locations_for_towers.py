import cv2

def get_tower_locations(video_path):
    state = {
        "drawing": False,
        "start": (0, 0),
        "current_rect": None,
        "paused": False
    }
    
    def _draw_callback(event, x, y, flags, param):
        if not state["paused"]:
            return
            
        if event == cv2.EVENT_LBUTTONDOWN:
            state["drawing"] = True
            state["start"] = (x, y)
            state["current_rect"] = None
        
        elif event == cv2.EVENT_MOUSEMOVE:
            if state["drawing"]:
                # Update current rectangle while dragging
                state["current_rect"] = (state["start"][0], state["start"][1], x, y)
        
        elif event == cv2.EVENT_LBUTTONUP:
            if state["drawing"]:
                # Calculate width and height
                ix, iy = state["start"][0], state["start"][1]
                width = abs(x - ix)
                height = abs(y - iy)
                
                # Store as (x_topleft, y_topleft, width, height)
                rect_coords = (min(ix, x), min(iy, y), width, height)
                state["rect_coords"] = rect_coords
                state["drawing"] = False
                state["current_rect"] = None
    
    cv2.namedWindow('Tower Locations')
    cv2.setMouseCallback("Tower Locations", _draw_callback)
    
    cap = cv2.VideoCapture(video_path)
    
    # Check if video opened successfully
    if not cap.isOpened():
        print(f"Error: Could not open video file at {video_path}")
        return
    
    # Read first frame to get dimensions
    ret, first_frame = cap.read()
    if not ret:
        print("Error: Could not read first frame")
        cap.release()
        return
    
    height, width = first_frame.shape[:2]
    print(f"Video dimensions: Width={width}, Height={height}")
    
    # Reset video to beginning
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    current_frame = None
    
    while True:
        if not state["paused"]:
            ret, frame = cap.read()
            if not ret:
                # Loop back to beginning if video ends
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            current_frame = frame.copy()
        
        # Draw bounding boxes on current frame
        display_frame = current_frame.copy()
        
        # Draw completed bounding box
        if "rect_coords" in state and state["rect_coords"]:
            x, y, w, h = state["rect_coords"]
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Draw current rectangle being drawn
        if state["current_rect"]:
            x1, y1, x2, y2 = state["current_rect"]
            cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        cv2.imshow('Tower Locations', display_frame)
        
        key = cv2.waitKey(15) & 0xFF
        
        if key == ord('p'):
            # Pause iteration
            state["paused"] = True
            print("Paused - You can now draw bounding boxes")
        
        elif key == ord('c'):
            # Continue/unpause iteration
            state["paused"] = False
            print("Continuing frame iteration...")
        
        elif key == ord('s'):
            # Save and print bounding box coordinates, then reset
            if "rect_coords" in state and state["rect_coords"]:
                x, y, w, h = state["rect_coords"]
                print(f"Bounding Box - Top Left: ({x}, {y}), Width: {w}, Height: {h}")
                # Reset drawings
                state.pop("rect_coords", None)
                state["current_rect"] = None
                state["drawing"] = False
                print("Drawings reset")
            else:
                print("No bounding box to save")
        
        elif key == ord('q'):
            # Quit
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    video_file_path = 'videos/recording_20260122_112250.mp4'
    get_tower_locations(video_file_path)