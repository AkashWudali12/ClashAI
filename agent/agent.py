import socket
from typing import Optional
import av
import cv2
import time
import subprocess
import threading
import numpy as np
# import xml.etree.ElementTree as ET

"""
This class is used to play Clash Royale.
"""

UI_STATE_FILE = "/data/local/tmp/t.xml"

class ClashAgent:
    def __init__(self, __adb_path="/Users/akashwudali/Library/Android/sdk/platform-tools/adb", __background_image_path="/Users/akashwudali/ClashAI/tower_images/background_image.png"):
        self.__video_socket: Optional[socket.socket] = None
        self.__control_socket: Optional[socket.socket] = None
        self.ready: bool = False

        self.__ADB_PATH = __adb_path

        self.__background_image = cv2.imread(__background_image_path)
        self.__arena_bounding_box = {
            "x": 45,
            "y": 105,
            "width": 488,
            "height": 664
        }

    def __setup_screen_recording_environment(self):
        """
        Sets up screen recording
        """
        pass
    
    def __highlight_differences(self, frame: np.ndarray) -> np.ndarray:
        """
        Subtracts background image from arena bounding box region and makes differences black.
        
        Args:
            frame: Current frame to process
            
        Returns:
            Updated frame with differences set to black
        """
        if self.__background_image is None or self.__arena_bounding_box is None:
            return frame
        
        # Create a copy to avoid modifying the original
        # updated_frame = frame.copy()
        
        # Extract bounding box coordinates
        x = self.__arena_bounding_box["x"]
        y = self.__arena_bounding_box["y"]
        w = self.__arena_bounding_box["width"]
        h = self.__arena_bounding_box["height"]
        
        # Extract ROI (Region of Interest) from current frame
        roi = frame[y:y+h, x:x+w]
        
        # Ensure background image matches ROI dimensions
        if self.__background_image.shape[:2] != roi.shape[:2]:
            bg_resized = cv2.resize(self.__background_image, (w, h), interpolation=cv2.INTER_AREA)
        else:
            bg_resized = self.__background_image
        
        # Calculate absolute difference between background and current ROI
        diff = cv2.absdiff(bg_resized, roi)
        
        # Convert to grayscale for thresholding
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        
        # Create binary mask for differences (threshold value similar to annotate_image.py)
        _, mask = cv2.threshold(gray_diff, 40, 255, cv2.THRESH_BINARY)
        
        # Set all differences to black (0, 0, 0)
        roi[mask == 255] = (0, 0, 0)
        
        # Update the frame with modified ROI
        frame[y:y+h, x:x+w] = roi
        
        return frame
    
    def __connect_socket(self) -> None:
        try:
            # 1. Establish Video Connection (First)
            self.__video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__video_socket.connect(('127.0.0.1', 27183))
            print("✅ Video Socket Connected")

            # 2. Establish Control Connection (Second)
            # Small delay helps the server distinguish the two incoming connections
            time.sleep(0.1) 
            self.__control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__control_socket.connect(('127.0.0.1', 27183))
            print("✅ Control Socket Connected")

            # 3. Read Device Metadata from the Video Socket
            # The server only sends this on the video channel
            device_name_raw = self.__video_socket.recv(64)
            device_name = device_name_raw.decode('utf-8', errors='ignore').strip('\x00')
            print(f"📱 Device Name: {device_name}")

            # 4. Read Video Header (Codec, Width, Height)
            header = self.__video_socket.recv(12)
            if len(header) == 12:
                print(f"📊 Header Received (Hex): {header.hex()}")
            else:
                print("⚠️ Header incomplete or delayed")
            
            self.ready = True

        except KeyboardInterrupt:
            print("\n👋 Stopping client...")
        except Exception as e:
            print(f"\n❗ Error: {e}")
        finally:
            if self.ready:
                print("Successfully created Android client")
            else:
                print("Failed to create Android client")
    
    def play(self):
        """
        Presses play and activates screen recording
        Runs main image processing loop
        """
        
        try:
            self.__connect_socket()
            if self.ready:
                print("Created Socket File")
                socket_file = self.__video_socket.makefile('rb', buffering=0)

                # Continuous Stream Loop
                print("Reading raw video data (Ctrl+C to stop)...")
                container = av.open(socket_file, format='h264')

                frame_count = 0
                for frame in container.decode(video=0):
                    frame_start = time.perf_counter()
                    
                    # Step 1: Decode frame (already done in for loop, measure conversion)
                    decode_start = time.perf_counter()
                    img = frame.to_ndarray(format='bgr24')
                    decode_time = (time.perf_counter() - decode_start) * 1000
                    
                    # Step 2: Process frame (highlight differences)
                    process_start = time.perf_counter()
                    new_img = img
                    # new_img = self.__highlight_differences(img)
                    process_time = (time.perf_counter() - process_start) * 1000
                    
                    # Step 3: Display frame
                    display_start = time.perf_counter()
                    cv2.imshow("Android Screen", new_img)
                    display_time = (time.perf_counter() - display_start) * 1000
                    
                    # Total frame processing time
                    total_time = (time.perf_counter() - frame_start) * 1000
                    
                    frame_count += 1
                    print("--------------------------------")
                    print(f"Frame {frame_count} - Decode: {decode_time:.2f}ms | "
                          f"Process: {process_time:.2f}ms | "
                          f"Display: {display_time:.2f}ms | "
                          f"Total: {total_time:.2f}ms")

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
            else:
                print("Could not connect to video socket")
        except KeyboardInterrupt:
            print("\n👋 Stopping client...")
        except Exception as e:
            print(f"\n❗ Error: {e}")

    def start_game(self):
        pass