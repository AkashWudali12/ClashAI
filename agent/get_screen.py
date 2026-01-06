import scrcpy
import time
import adbutils
import socket

client = scrcpy.Client(device="emulator-5554")

try:
    client.start(threaded=True)
    time.sleep(10) # Give it a second to try and connect
    print("Finished Delay")
    
    if not client.alive:
        print("The client failed to stay alive.")
        # Check if we can reach the device at all via ADB
        device = adbutils.adb.device(serial="emulator-5554")
        print(f"ADB sees device: {device.prop.name}")
    else:
        print(f"Client is alive: {client.alive}")
        if client.last_frame is None:
            print(client.device_name)
        else:
            print(f"Last frame received: {client.last_frame}")
except Exception as e:
    print(f"Caught an error during startup: {e}")
finally:
    client.stop()