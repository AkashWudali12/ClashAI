import cv2
import os
from datetime import datetime

# Tower bounding boxes from constants.py
# TOWER_BOXES = {
#     "enemy_left_tower": {"x": 92, "y": 124, "width": 87, "height": 125},
#     "enemy_right_tower": {"x": 390, "y": 126, "width": 98, "height": 130},
#     "enemy_king_tower": {"x": 229, "y": 23, "width": 113, "height": 158},
#     "user_left_tower": {"x": 96, "y": 568, "width": 85, "height": 105},
#     "user_right_tower": {"x": 387, "y": 577, "width": 94, "height": 94},
#     "user_king_tower": {"x": 225, "y": 627, "width": 121, "height": 165}
# }

TOWER_BOXES = {
    "battle_field": {"x": 45, "y": 105, "width": 488, "height": 664}
}

def extract_tower_images(video_path, output_dir="tower_images"):
    """
    Processes video and allows saving tower images by pressing 's'
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
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
    print("\nControls:")
    print("  's' - Save all tower images from current frame")
    print("  'q' - Quit")
    print()
    
    # Reset video to beginning
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            # Loop back to beginning if video ends
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            frame_count = 0
            continue
        
        frame_count += 1
        
        # Draw bounding boxes on frame
        display_frame = frame.copy()
        for tower_name, box in TOWER_BOXES.items():
            x = box["x"]
            y = box["y"]
            w = box["width"]
            h = box["height"]
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # Add label
            label = tower_name.replace("_", " ").title()
            cv2.putText(display_frame, label, (x, y - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        cv2.imshow('Tower Images Extractor', display_frame)
        
        key = cv2.waitKey(15) & 0xFF
        
        if key == ord('s'):
            # Save all tower images
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            saved_count = 0
            
            for tower_name, box in TOWER_BOXES.items():
                x = box["x"]
                y = box["y"]
                w = box["width"]
                h = box["height"]
                
                # Extract ROI (Region of Interest)
                roi = frame[y:y+h, x:x+w]
                
                if roi.size > 0:
                    # Create readable filename
                    filename = f"{tower_name}_{timestamp}_frame{frame_count}.png"
                    filepath = os.path.join(output_dir, filename)
                    
                    # Save image
                    cv2.imwrite(filepath, roi)
                    saved_count += 1
                    print(f"Saved: {filename}")
            
            print(f"\n✅ Saved {saved_count} tower images to '{output_dir}' directory\n")
        
        elif key == ord('q'):
            # Quit
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("Exiting...")

if __name__ == "__main__":
    video_file_path = 'videos/recording_20260122_115747.mp4'
    extract_tower_images(video_file_path)

