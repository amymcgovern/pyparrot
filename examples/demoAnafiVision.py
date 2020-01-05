"""FFmpeg based vision demo for Parrot Anafi"""
import threading
import time

import cv2
from pyparrot.Anafi import Anafi
from pyparrot.DroneVision import DroneVision
from pyparrot.Model import Model


# Set to True to output images
WRITE_IMAGES = False

class UserVision:
    def __init__(self, vision):
        self.index = 0
        self.vision = vision

    def save_pictures(self, args):
        img = self.vision.get_latest_valid_picture()
        if img is not None and WRITE_IMAGES:
            cv2.imwrite(f"image_{self.index:06d}.png", img)
            self.index += 1


if __name__ == "__main__":
    anafi = Anafi()

    if anafi.connect(num_retries=3):
        print("Anafi connected")

        # State information
        print("Updating state information")
        anafi.smart_sleep(1)
        anafi.ask_for_state_update()
        anafi.smart_sleep(1)

        # Vision
        print("Starting vision")
        anafi_vision = DroneVision(anafi, Model.ANAFI)
        user_vision = UserVision(anafi_vision)
        anafi_vision.set_user_callback_function(
            user_vision.save_pictures, user_callback_args=None
        )

        # Video feed
        if anafi_vision.open_video():
            print("Opened video feed")
            print("Sleeping for 15 seconds - move Anafi around to test feed")
            anafi.smart_sleep(15)
            print("Closing video feed")
            anafi_vision.close_video()
            anafi.smart_sleep(5)
        else:
            print("Could not open video feed")

        print("Anafi disconnected")
        anafi.disconnect()
    else:
        print("Could not connect to Anafi")
