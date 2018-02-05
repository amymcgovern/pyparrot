"""
Demo of the Bebop vision code (basically flies around and saves out photos as it flies)
"""
from Bebop import Bebop
from BebopVision import BebopVision
import threading
import cv2
import time

isAlive = False

class UserVision:
    def __init__(self, vision):
        self.index = 0
        self.vision = vision

    def save_pictures(self, args):
        print("saving picture")
        img = self.vision.get_latest_valid_picture()

        filename = "test_image_%06d.png" % self.index
        cv2.imwrite(filename, img)
        self.index +=1


# make my bebop object
bebop = Bebop()

# connect to the bebop
success = bebop.connect(5)

if (success):
    # start up the video
    bebopVision = BebopVision(bebop)

    userVision = UserVision(bebopVision)
    bebopVision.set_user_callback_function(userVision.save_pictures, user_callback_args=None)
    success = bebopVision.open_video(max_retries=15)

    if (success):
        print("Vision successfully started!")
        bebopVision.start_video_buffering()


    # skipping actually flying for safety purposes indoors - if you want
    # different pictures, move the bebop around by hand
    print("Fly me around by hand!")
    bebop.smart_sleep(5)

    bebopVision.stop_vision_buffering()
    bebop.disconnect()
else:
    print("Error connecting to bebop.  Retry")

