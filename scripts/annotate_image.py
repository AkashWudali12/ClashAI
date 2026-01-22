import cv2
import numpy as np

def preprocess(img, STD_WIDTH=720, STD_HEIGHT=1280):
    # Resize to standard dimensions
    img = cv2.resize(img, (STD_WIDTH, STD_HEIGHT), interpolation=cv2.INTER_AREA)
    # Convert to grayscale and blur to smooth out scaling noise
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.GaussianBlur(gray, (5, 5), 0)

def extract_play_by_play(video_path):
    state = { "drawing": False, "start": (0, 0) }
    def _draw_callback(event, x, y, flags, param):

        print(f"Current Event: {event}, {(cv2.EVENT_LBUTTONDOWN, cv2.EVENT_MOUSEMOVE, cv2.EVENT_LBUTTONUP)}")

        if state["drawing"]:

            if event == cv2.EVENT_LBUTTONDOWN:
                print("DOWN")
                state["start"] = (x, y)

            if event == cv2.EVENT_MOUSEMOVE:
                print("MOVE")
                # if state["drawing"]:
                #     # Create a copy so we don't "stack" rectangles while dragging
                #     cv2.rectangle(state["frame"], state["start"], (x, y), (0, 255, 0), 2)
                #     cv2.imshow("Draw Rectangle", state["frame"])

            if event == cv2.EVENT_LBUTTONUP:
                print("UP")
                
                # Calculate width and height
                ix, iy = state["start"][0], state["start"][1]
                width = abs(x - ix)
                height = abs(y - iy)

                # Store as (x_topleft, y_topleft, width, height)
                rect_coords = (min(ix, x), min(iy, y), width, height)
                state["rect_coords"] = rect_coords
                print(f"Box Stored: X={rect_coords[0]}, Y={rect_coords[1]}, W={width}, H={height}")

    cv2.namedWindow('draw')
    cv2.setMouseCallback("draw", _draw_callback)
    cap = cv2.VideoCapture(video_path)

    # Check if video opened successfully
    if not cap.isOpened():
        print(f"Error: Could not open video file at {video_path}")
        return
    
    iterating = True 

    while cap.isOpened:

        if iterating:
            ret, frame = cap.read()
            if not ret:
                break

            if "rect_coords" in state:
                x, y, w, h = state["rect_coords"]
                roi = frame[y : y+h, x : x+w]
                if "background" in state:
                    diff = cv2.absdiff(state["background"], roi)
                    gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                    _, mask = cv2.threshold(gray_diff, 40, 255, cv2.THRESH_BINARY)
                    highlighted_frame = roi.copy()
                    highlighted_frame[mask == 255] = (0, 255, 0)
                    cv2.imshow('Differences Highlighted', highlighted_frame)

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # press d to draw bounding box
            if cv2.waitKey(15) & 0xFF == ord('d'):
                state["drawing"] = True
                iterating = False
            
            if cv2.waitKey(15) & 0xFF == ord('q'):
                break
        else:
            if "rect_coords" in state:
                x, y, w, h = state["rect_coords"]
                state["background"] = frame[y : y+h, x : x+w]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            if cv2.waitKey(15) & 0xFF == ord('d'):
                state["drawing"] = False
                iterating = True
        
        cv2.imshow('draw', frame)
    
    cap.release()
    cv2.destroyAllWindows()

video_file_path = 'videos/vid_1.mp4' 
extract_play_by_play(video_file_path)