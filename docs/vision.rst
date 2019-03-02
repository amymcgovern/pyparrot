.. title:: Using Vision on the Mambos and Bebop

.. vision:

Using Vision on the Mambos and Bebop
====================================

The vision system uses a common interface for the Mambo and the Bebop.  There are two approaches to the vision.
The first relies on ffmpeg and the second on libVLC.  Both approaches assume opencv is also installed.
Note, the reason we do not simply rely on opencv directly is that there is a known existing bug in
opencv with RTSP streams that makes them unreliable.  The behavior we reliably saw by using opencv directly was
that the stream would open, obtain between 10 and 15 frames and then stop collecting any new frames.  Since
this is not tenable for flying, we bypass opencv's direct open of the stream with two other approaches described below.

Using ffmpeg for vision
-----------------------

`ffmpeg <https://www.ffmpeg.org>`_ is an open-source cross-platform library that can be used to process a
wide variety of video and audio streams.  We use ffmpeg to bypass the issue with opencv by opening the video stream
in ffmpeg. The advantage of this approach is that the ffmpeg encoder can read the raw video streams (RTSP for
Mambo and RTP for Bebop) and convert it directly to a format that opencv can easily read.  We chose to convert to png
format.  The disadvantage is that ffmpeg has to save the converted images to disk, which introduces a slight delay
to the image processing.  If you use a high-end laptop with a solid state drive, this delay can be as low as
0.5 seconds.  Lower-processing speed laptops can introduce longer delays.  However, if you want access to the images
after your flight or you do not need real-time access, this is the better choice.

The vision code itself can be found in
`DroneVision.py <https://github.com/amymcgovern/pyparrot/blob/master/pyparrot/DroneVision.py>`_.
Running this code requires both the ffmpeg software and the opencv package.  This approach does NOT show a
live stream of the vision to the user but you can visualize the images using
the `VisionServer.py <https://github.com/amymcgovern/pyparrot/blob/master/pyparrot/VisionServer.py>`_.

One thing to note:  since ffmpeg requires the images to be written to a folder, it will save images to a
directory named images inside the pyparrot package.  **You will want to clean this folder out after each flight!**


Mambo ffmpeg vision demo
^^^^^^^^^^^^^^^^^^^^^^^^

The demo code for the mambo, `demoMamboVision.py <https://github.com/amymcgovern/pyparrot/blob/master/examples/demoMamboVision.py>`_
shown below, has the mambo take off, move upwards for a short time, flip, and then land.
While all of this flight code is running, the vision processing is running in a separate thread.

The first highlighted line:

.. code-block:: python

    testFlying = False


can be changed to True to have the mambo fly or set to False to do the vision without the mambo moving.
**One big note:  if the mambo is NOT flying, it will turn the camera into a sleep mode after several minutes
and you either need to reboot the mambo or connect and takeoff to restart the camera.**

The highlighted line with the code:


.. code-block:: python

        mamboVision.set_user_callback_function(userVision.save_pictures, user_callback_args=None)


is where the user sets the function to be called with every new vision frame.  In this demo, the images are simply
read in and saved back to a new file name.


.. code-block:: python
    :emphasize-lines: 14, 54

    """
    Demo of the ffmpeg based mambo vision code (basically flies around and saves out photos as it flies)

    Author: Amy McGovern
    """
    from pyparrot.Mambo import Mambo
    from pyparrot.DroneVision import DroneVision
    import threading
    import cv2
    import time


    # set this to true if you want to fly for the demo
    testFlying = False

    class UserVision:
        def __init__(self, vision):
            self.index = 0
            self.vision = vision

        def save_pictures(self, args):
            print("in save pictures on image %d " % self.index)

            img = self.vision.get_latest_valid_picture()

            if (img is not None):
                filename = "test_image_%06d.png" % self.index
                cv2.imwrite(filename, img)
                self.index +=1
                #print(self.index)



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
        mamboVision = DroneVision(mambo, is_bebop=False, buffer_size=30)
        userVision = UserVision(mamboVision)
        mamboVision.set_user_callback_function(userVision.save_pictures, user_callback_args=None)
        success = mamboVision.open_video()
        print("Success in opening vision is %s" % success)

        if (success):
            print("Vision successfully started!")
            #removed the user call to this function (it now happens in open_video())
            #mamboVision.start_video_buffering()

            if (testFlying):
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
            else:
                print("Sleeeping for 15 seconds - move the mambo around")
                mambo.smart_sleep(15)

            # done doing vision demo
            print("Ending the sleep and vision")
            mamboVision.close_video()

            mambo.smart_sleep(5)

        print("disconnecting")
        mambo.disconnect()


Bebop ffmpeg vision demo
^^^^^^^^^^^^^^^^^^^^^^^^
The demo code for the bebop for the ffmpeg vision works nearly identically to the mambo demo except it does
not fly the bebop around.  Instead, it starts the camera and then sleeps for 30 seconds for the user to
move around or move the drone around.  This is intended as a safe demo for indoors.  It also moves
the camera around so that it is obvious the vision is recording different photos.  The code is
available at `demoBebopVision.py <https://github.com/amymcgovern/pyparrot/blob/master/examples/demoBebopVision.py>`_
and is shown below.  The highlighted line is again where the user sets the callback function of how to
process the vision frames.

Updated in Version 1.5.13: you can tell DroneVision to either remove all the old vision files (now the default)
or not by sending the parameter cleanup_old_images=True or False.

.. code-block:: python
    :emphasize-lines: 40

    """
    Demo of the Bebop ffmpeg based vision code (basically flies around and saves out photos as it flies)

    Author: Amy McGovern
    """
    from pyparrot.Bebop import Bebop
    from pyparrot.DroneVision import DroneVision
    import threading
    import cv2
    import time

    isAlive = False

    class UserVision:
        def __init__(self, vision):
            self.index = 0
            self.vision = vision

        def save_pictures(self, args):
            #print("saving picture")
            img = self.vision.get_latest_valid_picture()

            if (img is not None):
                filename = "test_image_%06d.png" % self.index
                #cv2.imwrite(filename, img)
                self.index +=1


    # make my bebop object
    bebop = Bebop()

    # connect to the bebop
    success = bebop.connect(5)

    if (success):
        # start up the video
        bebopVision = DroneVision(bebop, is_bebop=True)

        userVision = UserVision(bebopVision)
        bebopVision.set_user_callback_function(userVision.save_pictures, user_callback_args=None)
        success = bebopVision.open_video()

        if (success):
            print("Vision successfully started!")
            #removed the user call to this function (it now happens in open_video())
            #bebopVision.start_video_buffering()

            # skipping actually flying for safety purposes indoors - if you want
            # different pictures, move the bebop around by hand
            print("Fly me around by hand!")
            bebop.smart_sleep(5)

            print("Moving the camera using velocity")
            bebop.pan_tilt_camera_velocity(pan_velocity=0, tilt_velocity=-2, duration=4)
            bebop.smart_sleep(25)
            print("Finishing demo and stopping vision")
            bebopVision.close_video()

        # disconnect nicely so we don't need a reboot
        bebop.disconnect()
    else:
        print("Error connecting to bebop.  Retry")



Using libVLC for vision
-----------------------

Our second approach to vision relies on the libVLC library, which in turn relies on the VLC program.
`VLC <https://www.videolan.org/vlc/index.html>`_ is a cross-platform media player and libVLC is a python
interface to the VLC libraries.  This can be done entirely in memory (not writing out to disk as ffmpeg required),
which means that the delay is minimized.  If you have a need for the full image stream after your flight, you likely
should choose the ffmpeg approach. If you simply want to use the vision, this approach may work better for you
since you don't have the disk delay and you don't introduce the issues with the images subdirectory.
The other advantage of this approach is that you get a real-time video stream of what the drone is seeing.  However,
controlling the drone after vision has started requires setting a new parameter called user_code_to_run, as shown
below and in the highlighted line in the demo code.

.. code-block:: python

        mamboVision = DroneVisionGUI(mambo, is_bebop=False, buffer_size=200,
                                     user_code_to_run=demo_mambo_user_vision_function, user_args=(mambo, ))


**To make this approach work, you MUST install the VLC client version 3.0.1 or greater.**
Installing only libvlc is not needed (the source is included with pyparrot) and it will not work.
Installing the client installs extra software that the libvlc python library requires.

There are two example programs, one for the bebop and one for the mambo.  Both show the window opened by this
approach and the way that a user can run their own code by assigning code to the Run button.

libVLC demo code for the Mambo
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This code can be downloaded from
`demoMamboVisionGUI.py <https://github.com/amymcgovern/pyparrot/blob/master/examples/demoMamboVisionGUI.py>`_
and is repeated below.

.. code-block:: python
    :emphasize-lines: 93, 94

    """
    Demo of the Bebop vision using DroneVisionGUI that relies on libVLC.  It is a different
    multi-threaded approach than DroneVision

    Author: Amy McGovern
    """
    from pyparrot.Mambo import Mambo
    from pyparrot.DroneVisionGUI import DroneVisionGUI
    import cv2


    # set this to true if you want to fly for the demo
    testFlying = True

    class UserVision:
        def __init__(self, vision):
            self.index = 0
            self.vision = vision

        def save_pictures(self, args):
            # print("in save pictures on image %d " % self.index)

            img = self.vision.get_latest_valid_picture()

            if (img is not None):
                filename = "test_image_%06d.png" % self.index
                # uncomment this if you want to write out images every time you get a new one
                #cv2.imwrite(filename, img)
                self.index +=1
                #print(self.index)


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
            mamboVision = DroneVisionGUI(mambo, is_bebop=False, buffer_size=200,
                                         user_code_to_run=demo_mambo_user_vision_function, user_args=(mambo, ))
            userVision = UserVision(mamboVision)
            mamboVision.set_user_callback_function(userVision.save_pictures, user_callback_args=None)
            mamboVision.open_video()



libVLC demo code for the Bebop
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This code can be downloaded from
`demoBebopVision.py <https://github.com/amymcgovern/pyparrot/blob/master/examples/demoBebopVisionGUI.py>`_
and is repeated below.

.. code-block:: python
    :emphasize-lines: 69,70

    """
    Demo of the Bebop vision using DroneVisionGUI (relies on libVLC).  It is a different
    multi-threaded approach than DroneVision

    Author: Amy McGovern
    """
    from pyparrot.Bebop import Bebop
    from pyparrot.DroneVisionGUI import DroneVisionGUI
    import threading
    import cv2
    import time

    isAlive = False

    class UserVision:
        def __init__(self, vision):
            self.index = 0
            self.vision = vision

        def save_pictures(self, args):
            #print("saving picture")
            img = self.vision.get_latest_valid_picture()

            if (img is not None):
                filename = "test_image_%06d.png" % self.index
                #cv2.imwrite(filename, img)
                self.index +=1


    def demo_user_code_after_vision_opened(bebopVision, args):
        bebop = args[0]

        print("Vision successfully started!")
        #removed the user call to this function (it now happens in open_video())
        #bebopVision.start_video_buffering()

        # takeoff
        bebop.safe_takeoff(5)

        # skipping actually flying for safety purposes indoors - if you want
        # different pictures, move the bebop around by hand
        print("Fly me around by hand!")
        bebop.smart_sleep(5)

        if (bebopVision.vision_running):
            print("Moving the camera using velocity")
            bebop.pan_tilt_camera_velocity(pan_velocity=0, tilt_velocity=-2, duration=4)
            bebop.smart_sleep(5)

            # land
            bebop.safe_land(5)

            print("Finishing demo and stopping vision")
            bebopVision.close_video()

        # disconnect nicely so we don't need a reboot
        print("disconnecting")
        bebop.disconnect()

    if __name__ == "__main__":
        # make my bebop object
        bebop = Bebop()

        # connect to the bebop
        success = bebop.connect(5)

        if (success):
            # start up the video
            bebopVision = DroneVisionGUI(bebop, is_bebop=True, user_code_to_run=demo_user_code_after_vision_opened,
                                         user_args=(bebop, ))

            userVision = UserVision(bebopVision)
            bebopVision.set_user_callback_function(userVision.save_pictures, user_callback_args=None)
            bebopVision.open_video()

        else:
            print("Error connecting to bebop.  Retry")


