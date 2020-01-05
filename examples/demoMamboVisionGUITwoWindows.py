"""
Demo of the Mambo vision using DroneVisionGUI that relies on libVLC and shows how to make a
second window using opencv to draw on the processed window.  It is a different
multi-threaded approach than DroneVision

Author: Amy McGovern
"""
from pyparrot.Minidrone import Mambo
from pyparrot.DroneVisionGUI import DroneVisionGUI
from pyparrot.Model import Model
import cv2
import time


# set this to true if you want to fly for the demo
testFlying = True
font = cv2.FONT_HERSHEY_SIMPLEX

def draw_second_pictures(args):
    """
    Grab the latest stream from the drone and draw it in a second opencv window with some text to show that it
    is being processed

    :param args:
    :return:
    """

    # get the vision
    mamboVision = args[0]

    # get the latest images
    img = mamboVision.get_latest_valid_picture()

    # if the images is invalid, return
    if(img is None):
        return

    # put the roll and pitch at the top of the screen
    cv2.putText(img, 'demo text', (50, 50), font, 1, (255, 0, 255), 2, cv2.LINE_AA)
    cv2.imshow("MarkerStream", img)

def demo_mambo_user_vision_function(mamboVision, args):
    """
    Demo the user code to run with the run button for a mambo

    :param args:
    :return:
    """
    mambo = args[0]

    if (testFlying):
        print("taking off!")
        mambo.safe_takeoff(5)

        if (mambo.sensors.flying_state != "emergency"):
            print("flying state is %s" % mambo.sensors.flying_state)
            print("Flying direct: going up")
            mambo.fly_direct(roll=0, pitch=0, yaw=0, vertical_movement=15, duration=2)

            print("flip left")
            print("flying state is %s" % mambo.sensors.flying_state)
            success = mambo.flip(direction="left")
            print("mambo flip result %s" % success)
            mambo.smart_sleep(5)

        print("landing")
        print("flying state is %s" % mambo.sensors.flying_state)
        mambo.safe_land(5)
    else:
        print("Sleeeping for 15 seconds - move the mambo around")
        mambo.smart_sleep(15)

    # done doing vision demo
    print("Ending the sleep and vision")
    mamboVision.close_video()

    mambo.smart_sleep(5)

    print("disconnecting")
    mambo.disconnect()


if __name__ == "__main__":
    # make my mambo object
    # remember to set True/False for the wifi depending on if you are using the wifi or the BLE to connect
    # the address can be empty if you are using wifi
    mambo = Mambo(address="", use_wifi=True)
    print("trying to connect to mambo now")

    success = mambo.connect(num_retries=3)
    print("connected: %s" % success)

    if (success):
        # get the state information
        print("sleeping")
        mambo.smart_sleep(1)
        mambo.ask_for_state_update()
        mambo.smart_sleep(1)

        # setup the extra window to draw the markers in
        cv2.namedWindow("ExampleWindow")

        print("Preparing to open vision")
        mamboVision = DroneVisionGUI(mambo, Model.MAMBO, buffer_size=200,
                                     user_code_to_run=demo_mambo_user_vision_function, user_args=(mambo, ))

        mamboVision.set_user_callback_function(draw_second_pictures, user_callback_args=(mamboVision, ))
        mamboVision.open_video()
