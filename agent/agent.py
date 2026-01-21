import socket
from typing import Optional
import av
import cv2
import time
import subprocess
import threading
# import xml.etree.ElementTree as ET

"""
This class is used to play Clash Royale.
"""

UI_STATE_FILE = "/data/local/tmp/t.xml"

class ClashAgent:
    def __init__(self, __adb_path="/Users/akashwudali/Library/Android/sdk/platform-tools/adb"):
        self.__video_socket: Optional[socket.socket] = None
        self.__control_socket: Optional[socket.socket] = None
        self.ready: bool = False

        self.__ADB_PATH = __adb_path

    def __setup_screen_recording_environment(self):
        """
        Sets up screen recording
        """
        pass
    
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

                for frame in container.decode(video=0):
                    img = frame.to_ndarray(format='bgr24')
                    cv2.imshow("Android Screen", img)

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