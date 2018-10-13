.. title:: Quick Start with a Minidrone

.. quickstartmambo:

Quick Start Guide with a Minidrone
==============================

Using the pyparrot library on the Minidrone
---------------------------------------

Before running any of the sample code, you will need to connect to your drone.  If you have a Mambo FPV, I highly
recommend using the wifi connection since it sends much more information using wifi than BLE.  If you have a Mambo Code
or a Mambo Fly or Swing(neither of which has a camera), then you need to use the BLE connection.

wifi connection
^^^^^^^^^^^^^^^

If you are using the wifi (e.g. Mambo FPV), you need to connect your controlling device (laptop, computer, etc)
to the wifi for the drone.  Look for a wifi network named Mambo_number where number changes for each drone.

BLE connection
^^^^^^^^^^^^^^

If you do not have a camera or want to use BLE for other reasons(e.g. swarm), you will first need to find the
BLE address of your Minidrone(s).  BLE permissions on linux require that this command run in sudo mode.
To run this, from the bin directory for your python installation, type:

::

    sudo findMinidrone


This will identify all BLE devices within hearing of the Pi.  The Minidrone's specific address will be printed at the end.
Save the address and use it in your connection code (discussed below).  If findMinidrone does not
report "FOUND A MAMBO!" or "FOUND A SWING!", then be sure your minidrone is turned on when you run the findMambo code and that your Pi
(or other linux box) has its BLE interface turned on.

The output should look something like this.  I removed my own BLE addresses from my network for security but I am
showing the address of the mambo that I use for all the demo scripts.

.. code-block:: console

    ~/miniconda3/bin $ sudo ./find_mambo
    Discovered device <address removed>
    Discovered device <address removed>
    Discovered device <address removed>
    Discovered device e0:14:d0:63:3d:d0
    Received new data from <address removed>
    Discovered device <address removed>
    Discovered device <address removed>
    Received new data from <address removed>
    Discovered device <address removed>
    FOUND A MAMBO!
    Device e0:14:d0:63:3d:d0 (random), RSSI=-60 dB
      Complete Local Name = Mambo_<numbers>



Quick start:  Demo Code
-----------------------

I have provided a set of `example <https://github.com/amymcgovern/pyparrot/tree/master/examples>`_ scripts for both the
Mambo and the Bebop.  Note that you will need to edit the minidrone scripts to either use your own BLE address or to
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

    """
    Demo the trick flying for the python interface

    Author: Amy McGovern
    """

    from pyparrot.Minidrone import Mambo

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

    """
    Demo the direct flying for the python interface

    Author: Amy McGovern
    """

    from pyparrot.Minidrone import Mambo

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

    """
    Demo the claw for the python interface

    Author: Amy McGovern
    """

    from pyparrot.Minidrone import Mambo

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

    """
    Demo the gun for the python interface

    Author: Amy McGovern
    """

    from pyparrot.Minidrone import Mambo

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
    Author: Amy McGovern
    """

    from pyparrot.Minidrone import Mambo
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

        # take the photo
        pic_success = mambo.take_picture()

        # need to wait a bit for the photo to show up
        mambo.smart_sleep(0.5)

        picture_names = mambo.groundcam.get_groundcam_pictures_names() #get list of availible files
        print(picture_names)

        frame = mambo.groundcam.get_groundcam_picture(picture_names[0],True) #get frame which is the first in the array

        if frame is not None:
            if frame is not False:
                cv2.imshow("Groundcam", frame)
                cv2.waitKey(100)

        mambo.safe_land(5)
        mambo.disconnect()

Demo of the flying mode on the swing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
`demoSwingDirectFlight.py <https://github.com/amymcgovern/pyparrot/blob/master/examples/demoSwingDirectFlight.py>`_
You can see how to use the set_flying_mode command. I advise you to have enough space to use this script.

.. code-block:: python

    """
    Demo the direct flying for the python interface

    Author: Victor804
    """

    from pyparrot.Minidrone import Swing

    # you will need to change this to the address of YOUR swing
    swingAddr = "e0:14:04:a7:3d:cb"

    # make my swing object
    swing = Swing(swingAddr)

    print("trying to connect")
    success = swing.connect(num_retries=3)
    print("connected: %s" % success)

    if (success):
        # get the state information
        print("sleeping")
        swing.smart_sleep(2)
        swing.ask_for_state_update()
        swing.smart_sleep(2)

        print("taking off!")
        swing.safe_takeoff(5)

        print("plane forward")
        swing.set_flying_mode("plane_forward")

        swing.smart_sleep(1)

        print("quadricopter")
        swing.set_flying_mode("quadricopter")

        print("landing")
        swing.safe_land(5)
       swing.smart_sleep(5)

       print("disconnect")
       swing.disconnect()
       

Demo joystick for Swing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
`demoSwingJoystick.py <https://github.com/amymcgovern/pyparrot/blob/master/examples/demoSwingJoystick.py>`_
Example code to control the swig with a joystick. Easy to modify for your needs.

.. code-block:: python


    import pygame
    import sys
    from pyparrot.Minidrone import Swing

    def joystick_init():
        """
        Initializes the controller, allows the choice of the controller.
        If no controller is detected returns an error.

        :param:
        :return joystick:
        """
        pygame.init()
        pygame.joystick.init()

        joystick_count = pygame.joystick.get_count()

        if joystick_count > 0:
            for i in range(joystick_count):
                joystick = pygame.joystick.Joystick(i)
                joystick.init()

                name = joystick.get_name()
                print([i], name)

                joystick.quit()

        else:
            sys.exit("Error: No joystick detected")

        selected_joystick = eval(input("Enter your joystick number:"))

        if selected_joystick not in range(joystick_count):
            sys.exit("Error: Your choice is not valid")

        joystick = pygame.joystick.Joystick(selected_joystick)
        joystick.init()

        return joystick


    def mapping_button(joystick, dict_commands):
        """
        Associating a controller key with a command in dict_commands.

        :param joystick, dict_commands:
        :return mapping:
        """
        mapping = {}

        for command in dict_commands:
            print("Press the key", command)
            done = False
            while not done:
                for event in pygame.event.get():
                    if event.type == pygame.JOYBUTTONDOWN:
                        if event.button not in (value for value in mapping.values()):
                            mapping[command] = event.button
                            done = True

        return mapping


    def mapping_axis(joystick, axes=["pitch", "roll", "yaw", "vertical"]):
        """
        Associating the analog thumbsticks of the controller with a command in dict commands

        :param joystick, dict_commands:
        :return mapping:
        """
        mapping = {}

        for i in axes:
            print("Push the", i, "axis")
            done = False
            while not done:
                for event in pygame.event.get():
                    if event.type == pygame.JOYAXISMOTION:
                        if event.axis not in (value for value in mapping.values()):
                            mapping[i] = event.axis
                            done = True

        return mapping


    def _parse_button(dict_commands, button):
        """
        Send the commands to the drone.
        If multiple commands are assigned to a key each command will be sent one by one to each press.

        :param dict_commands, button:
        :return:
        """
        commands = dict_commands[button][0]
        args = dict_commands[button][-1]

        command = commands[0]
        arg = args[0]

        if len(commands) == 1:
            if len(args) == 1:
                command(arg)

            else:
                command(arg)
                dict_commands[button][-1] = args[1:]+[arg]

        else:
            if len(commands) == 1:
                command(arg)
                dict_commands[button][0] = commands[1:]+[command]

            else:
                command(arg)
                dict_commands[button][0] = commands[1:]+[command]
                dict_commands[button][-1] = args[1:]+[arg]


    def main_loop(joystick, dict_commands, mapping_button, mapping_axis):
        """
        First connects to the drone and makes a flat trim.
        Then in a loop read the events of the controller to send commands to the drone.

        :param joystick, dict_commands, mapping_button, mapping_axis:
        :return:
        """
        swing.connect(10)
        swing.flat_trim()

        while True:
            pygame.event.get()

            pitch = joystick.get_axis(mapping_axis["pitch"])*-100
            roll = joystick.get_axis(mapping_axis["roll"])*100
            yaw = joystick.get_axis(mapping_axis["yaw"])*100
            vertical = joystick.get_axis(mapping_axis["vertical"])*-100

            swing.fly_direct(roll, pitch, yaw, vertical, 0.1)

            for button, value in mapping_button.items():
                if joystick.get_button(value):
                    _parse_button(dict_commands, button)


    if __name__ == "__main__":
        swing = Swing("e0:14:04:a7:3d:cb")

        #Example of dict_commands
        dict_commands = {
                            "takeoff_landing":[ #Name of the button
                                                [swing.safe_takeoff, swing.safe_land],#Commands execute one by one
                                                [5]#Argument for executing the function
                                               ],
                            "fly_mode":[
                                        [swing.set_flying_mode],
                                        ["quadricopter", "plane_forward"]
                                       ],
                            "plane_gear_box_up":[
                                                 [swing.set_plane_gear_box],
                                                 [((swing.sensors.plane_gear_box[:-1]+str(int(swing.sensors.plane_gear_box[-1])+1)) if swing.sensors.plane_gear_box[-1] != "3" else "gear_3")]#"gear_1" => "gear_2" => "gear_3"
                                                ],
                            "plane_gear_box_down":[
                                                   [swing.set_plane_gear_box],
                                                   [((swing.sensors.plane_gear_box[:-1]+str(int(swing.sensors.plane_gear_box[-1])-1)) if swing.sensors.plane_gear_box[-1] != "1" else "gear_1")]#"gear_3" => "gear_2" => "gear_1"
                                                ]
                        }

        joystick = joystick_init()

        mapping_button = mapping_button(joystick, dict_commands)
        mapping_axis = mapping_axis(joystick)

        main_loop(joystick, dict_commands, mapping_button, mapping_axis)
