.. title:: Quick Start with a Mambo

.. quickstartmambo:

Quick Start Guide with a Mambo
==============================

Using the pyparrot library on the Mambo
---------------------------------------

Before running any of the sample code, you will need to connect to your drone.  If you have a Mambo FPV, I highly
recommend using the wifi connection since it sends much more information using wifi than BLE.  If you have a Mambo Code
or a Mambo Fly (neither of which has a camera), then you need to use the BLE connection.

wifi connection
^^^^^^^^^^^^^^^

If you are using the wifi (e.g. Mambo FPV), you need to connect your controlling device (laptop, computer, etc)
to the wifi for the drone.  Look for a wifi network named Mambo_number where number changes for each drone.

BLE connection
^^^^^^^^^^^^^^

If you do not have a camera or want to use BLE for other reasons(e.g. swarm), you will first need to find the
BLE address of your Mambo(s).  BLE permissions on linux require that this command run in sudo mode.
To this this, from the directory where you installed the pyparrot code, type:

::

    sudo python findMambo.py


This will identify all BLE devices within hearing of the Pi.  The Mambo's specific address will be printed at the end.
Save the address and use it in your connection code (discussed below).  If findMambo does not
report "FOUND A MAMBO!", then be sure your Mambo is turned on when you run the findMambo code and that your Pi
(or other linux box) has its BLE interface turned on.

The output should look something like this.

.. code-block:: console

    dumping object inventory... done
    build succeeded, 43 warnings.

    The HTML pages are in _build/html.
    defiant:docs>

    PUT ACTUAL OUTPUT HERE



Quick start:  Demo Code
-----------------------

I have provided a set of `example <https://github.com/amymcgovern/pyparrot/tree/master/examples>`_ scripts for both the
Mambo and the Bebop.  Note that you will need to edit the mambo scripts to either use your own BLE address or to
ensure that use_wifi=True is set, so that it connects using wifi.
**Note that you do not need to run any of the other code in sudo mode!**  That was only for discovery.

Demo of the trick commands on the mambo
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The code shown below is the
`demoMamboTricks.py <https://github.com/amymcgovern/pyparrot/blob/master/examples/demoMamboTricks.py>`_.
demoMamboTricks.py will take off, demonstrate all 4 types of flips, and then land.  It is a good program to
verify that your connection to your mambo is working well.  Be sure to run it in a room large enough
to perform the flips!  The highlighted lines need to change for YOUR mambo and connection choices.


.. code-block:: python
    :emphasize-lines: 10,14

    """
    Demo the trick flying for the python interface

    Author: Amy McGovern
    """

    from pyparrot.Mambo import Mambo

    # you will need to change this to the address of YOUR mambo
    mamboAddr = "e0:14:d0:63:3d:d0"

    # make my mambo object
    # remember to set True/False for the wifi depending on if you are using the wifi or the BLE to connect
    mambo = Mambo(mamboAddr, use_wifi=True)

    print("trying to connect")
    success = mambo.connect(num_retries=3)
    print("connected: %s" % success)

    if (success):
        # get the state information
        print("sleeping")
        mambo.smart_sleep(2)
        mambo.ask_for_state_update()
        mambo.smart_sleep(2)

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

            print("flip right")
            print("flying state is %s" % mambo.sensors.flying_state)
            success = mambo.flip(direction="right")
            print("mambo flip result %s" % success)
            mambo.smart_sleep(5)

            print("flip front")
            print("flying state is %s" % mambo.sensors.flying_state)
            success = mambo.flip(direction="front")
            print("mambo flip result %s" % success)
            mambo.smart_sleep(5)

            print("flip back")
            print("flying state is %s" % mambo.sensors.flying_state)
            success = mambo.flip(direction="back")
            print("mambo flip result %s" % success)
            mambo.smart_sleep(5)

            print("landing")
            print("flying state is %s" % mambo.sensors.flying_state)
            mambo.safe_land(5)
            mambo.smart_sleep(5)

        print("disconnect")
        mambo.disconnect()




Demo of the direct flight commands on the mambo
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The second example program shows how to directly fly the mambo by controlling the yaw, pitch, roll, and
vertical movement parameters.  **Make sure you try this one in a large enough room!**
This code is provided in
`demoMamboDirectFlight.py <https://github.com/amymcgovern/pyparrot/blob/master/examples/demoMamboDirectFlight.py>`_
and is also shown below.  Again, the highlighted lines must be changed to the parameters for your mambo and connection.

.. code-block:: python
    :emphasize-lines: 10,14

    """
    Demo the direct flying for the python interface

    Author: Amy McGovern
    """

    from pyparrot.Mambo import Mambo

    # you will need to change this to the address of YOUR mambo
    mamboAddr = "e0:14:d0:63:3d:d0"

    # make my mambo object
    # remember to set True/False for the wifi depending on if you are using the wifi or the BLE to connect
    mambo = Mambo(mamboAddr, use_wifi=True)

    print("trying to connect")
    success = mambo.connect(num_retries=3)
    print("connected: %s" % success)

    if (success):
        # get the state information
        print("sleeping")
        mambo.smart_sleep(2)
        mambo.ask_for_state_update()
        mambo.smart_sleep(2)

        print("taking off!")
        mambo.safe_takeoff(5)

        print("Flying direct: going forward (positive pitch)")
        mambo.fly_direct(roll=0, pitch=50, yaw=0, vertical_movement=0, duration=1)

        print("Showing turning (in place) using turn_degrees")
        mambo.turn_degrees(90)
        mambo.smart_sleep(2)
        mambo.turn_degrees(-90)
        mambo.smart_sleep(2)

        print("Flying direct: yaw")
        mambo.fly_direct(roll=0, pitch=0, yaw=50, vertical_movement=0, duration=1)

        print("Flying direct: going backwards (negative pitch)")
        mambo.fly_direct(roll=0, pitch=-50, yaw=0, vertical_movement=0, duration=0.5)

        print("Flying direct: roll")
        mambo.fly_direct(roll=50, pitch=0, yaw=0, vertical_movement=0, duration=1)

        print("Flying direct: going up")
        mambo.fly_direct(roll=0, pitch=0, yaw=0, vertical_movement=50, duration=1)

        print("Flying direct: going around in a circle (yes you can mix roll, pitch, yaw in one command!)")
        mambo.fly_direct(roll=25, pitch=0, yaw=50, vertical_movement=0, duration=3)

        print("landing")
        mambo.safe_land(5)
        mambo.smart_sleep(5)

        print("disconnect")
        mambo.disconnect()



Demo of the USB claw accessory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If your mambo has the USB accessories (claw and gun), you can control them but you *MUST* be in BLE mode.
The mambo can only handle one USB accessory at a time and the camera counts as a USB accessory so you must use
the BLE connection only.  `demoMamboClaw.py <https://github.com/amymcgovern/pyparrot/blob/master/examples/demoMamboClaw.py>`_
show how to use the claw accessory. The highlighted line must be changed to the BLE address for your mambo and the use_wifi
parameter must stay at False.  In this demo program, the mambo takes off, opens and closes the claw, and lands again.

.. code-block:: python
    :emphasize-lines: 10

    """
    Demo the claw for the python interface

    Author: Amy McGovern
    """

    from pyparrot.Mambo import Mambo

    # you will need to change this to the address of YOUR mambo
    mamboAddr = "e0:14:d0:63:3d:d0"

    # make my mambo object
    # remember you can't use the claw with the camera installed so this must be BLE connected to work
    mambo = Mambo(mamboAddr, use_wifi=False)

    print("trying to connect")
    success = mambo.connect(num_retries=3)
    print("connected: %s" % success)

    # get the state information
    print("sleeping")
    mambo.smart_sleep(2)
    mambo.ask_for_state_update()
    mambo.smart_sleep(2)

    print("taking off!")
    mambo.safe_takeoff(5)

    print("open and close the claw")
    mambo.open_claw()
    # you have to sleep to let the claw open (it needs time to do it)
    mambo.smart_sleep(5)

    mambo.close_claw()
    # you have to sleep to let the claw close (it needs time to do it)
    mambo.smart_sleep(5)

    print("landing")
    mambo.safe_land(5)
    mambo.smart_sleep(5)

    print("disconnect")
    mambo.disconnect()

Demo of the USB gun accessory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`demoMamboGun.py <https://github.com/amymcgovern/pyparrot/blob/master/examples/demoMamboGun.py>`_
show how to use the gun accessory. The highlighted line must be changed to the BLE address for your mambo and the use_wifi
parameter must stay at False.  In this demo program, the mambo takes off, fires the gun, and lands again.

.. code-block:: python
    :emphasize-lines: 10

    """
    Demo the gun for the python interface

    Author: Amy McGovern
    """

    from pyparrot.Mambo import Mambo

    # you will need to change this to the address of YOUR mambo
    mamboAddr = "e0:14:d0:63:3d:d0"

    # make my mambo object
    # remember you can't use the gun with the camera installed so this must be BLE connected to work
    mambo = Mambo(mamboAddr, use_wifi=False)

    print("trying to connect")
    success = mambo.connect(num_retries=3)
    print("connected: %s" % success)

    # get the state information
    print ("sleeping")
    mambo.smart_sleep(2)
    mambo.ask_for_state_update()
    mambo.smart_sleep(2)

    print("shoot the gun")
    mambo.fire_gun()

    # sleep to ensure it does the firing
    mambo.smart_sleep(15)

    print("disconnect")
    mambo.disconnect()



Demo of the ground-facing camera
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`demoMamboGroundcam.py <https://github.com/amymcgovern/pyparrot/blob/master/examples/demoMamboGroundcam.py>`_
show how to use the mambo's ground-facing camera.  This feature **ONLY** works in wifi mode.  It can be slow
to download the frames so do not count on this running at several frames per second.  The example code shown
below takes off, takes a picture, and then grabs a random picture from the ground facing camera set.

.. code-block:: python

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
