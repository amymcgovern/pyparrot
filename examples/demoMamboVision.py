"""
Demo of the mambo vision code (basically flies around and saves out photos as it flies)
"""
from Mambo import Mambo
from MamboVision import MamboVision
import threading
import cv2
import time

isAlive = False

class UserVision:
    def __init__(self, vision):
        self.index = 0
        self.vision = vision

    def save_pictures(self, args):
        img = self.vision.get_latest_valid_picture()

        filename = "test_image_%06d.png" % self.index
        cv2.imwrite(filename, img)
        self.index +=1



# you will need to change this to the address of YOUR mambo
mamboAddr = "e0:14:d0:63:3d:d0"

# make my mambo object
# remember to set True/False for the wifi depending on if you are using the wifi or the BLE to connect
mambo = Mambo(mamboAddr, use_wifi=True)
print("trying to connect to mambo now")
success = mambo.connect(num_retries=3)
print("connected: %s" % success)

if (success):
    # get the state information
    print("sleeping")
    mambo.smart_sleep(1)
    mambo.ask_for_state_update()
    mambo.smart_sleep(1)

    print("Preparing to open vision")
    mamboVision = MamboVision(buffer_size=10)
    userVision = UserVision(mamboVision)
    mamboVision.set_user_callback_function(userVision.save_pictures, user_callback_args=None)
    success = mamboVision.open_video(max_retries=15)

    if (success):
        print("Vision successfully started!")
        mamboVision.start_video_buffering()

    print("taking off!")
    mambo.safe_takeoff(5)

    if (mambo.sensors.flying_state != "emergency"):
        print("flying state is %s" % mambo.sensors.flying_state)
        print("Flying direct: going up")
        mambo.fly_direct(roll=0, pitch=0, yaw=0, vertical_movement=20, duration=1)

        print("flip left")
        print("flying state is %s" % mambo.sensors.flying_state)
        success = mambo.flip(direction="left")
        print("mambo flip result %s" % success)
        mambo.smart_sleep(5)

    print("landing")
    print("flying state is %s" % mambo.sensors.flying_state)
    mambo.safe_land(5)
    mamboVision.stop_vision_buffering()

    isAlive = False
    mambo.smart_sleep(5)

    print("disconnect")
    mambo.disconnect()
