"""
Demo of the groundcam
Mambo takes off, takes a picture and shows a RANDOM frame, not the last one
Author: Valentin Benke, https://github.com/Vabe7
"""

from pyparrot.Mambo import Mambo
import cv2

mambo = Mambo(None, use_wifi=True) #address is None since it only works with WiFi anyway
print("trying to connect to mambo now")
success = mambo.connect(num_retries=3)
print("connected: %s" % success)

if (success):
    # get the state information
    print("sleeping")
    mambo.smart_sleep(1)
    mambo.ask_for_state_update()
    mambo.smart_sleep(1)
    mambo.safe_takeoff(5)
    mambo.take_picture()
    list = mambo.groundcam.get_groundcam_pictures_names() #get list of availible files
    frame = mambo.groundcam.get_groundcam_picture(list[0],True) #get frame which is the first in the array
    if frame is not None:
        if frame is not False:
            cv2.imshow("Groundcam", frame)
            cv2.waitKey(100)

    mambo.safe_land(5)
    mambo.disconnect()
