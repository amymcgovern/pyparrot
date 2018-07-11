.. title:: Quick Start with a Bebop

.. quickstartmambo:

Quick Start Guide with a Bebop
==============================

Using the pyparrot library on the Bebop
---------------------------------------

Before running any of the sample code, you will need to connect to your drone.  To control the Bebop, you need to
connect your controlling device (laptop, computer, etc) to the wifi for the drone.  Look for the wifi network
named Bebop_number where number varies for each drone.

Quick start:  Demo Code
-----------------------
I have provided a set of `example <https://github.com/amymcgovern/pyparrot/tree/master/examples>`_ scripts for both the
Mambo and the Bebop.

Demo of the trick commands on the bebop
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The code shown below is the
`demoBebopTricks.py <https://github.com/amymcgovern/pyparrot/blob/master/examples/demoBebopTricks.py>`_.
demoBebopTricks.py will take off, demonstrate all 4 types of flips, and then land.  It is a good program to
verify that your connection to your bebop is working well.  The bebop can flip just like the Mambo!  This does
the exact same thing as the Mambo tricks demo: take off, flip in all 4 directions, land.
**Be sure to run it in a room large enough to perform the flips!**

.. code-block:: python

    """
    Demos the tricks on the bebop. Make sure you have enough room to perform them!

    Author: Amy McGovern
    """

    from pyparrot.Bebop import Bebop

    bebop = Bebop()

    print("connecting")
    success = bebop.connect(10)
    print(success)

    print("sleeping")
    bebop.smart_sleep(5)

    bebop.ask_for_state_update()

    bebop.safe_takeoff(10)

    print("flip left")
    print("flying state is %s" % bebop.sensors.flying_state)
    success = bebop.flip(direction="left")
    print("mambo flip result %s" % success)
    bebop.smart_sleep(5)

    print("flip right")
    print("flying state is %s" % bebop.sensors.flying_state)
    success = bebop.flip(direction="right")
    print("mambo flip result %s" % success)
    bebop.smart_sleep(5)

    print("flip front")
    print("flying state is %s" % bebop.sensors.flying_state)
    success = bebop.flip(direction="front")
    print("mambo flip result %s" % success)
    bebop.smart_sleep(5)

    print("flip back")
    print("flying state is %s" % bebop.sensors.flying_state)
    success = bebop.flip(direction="back")
    print("mambo flip result %s" % success)
    bebop.smart_sleep(5)

    bebop.smart_sleep(5)
    bebop.safe_land(10)

    print("DONE - disconnecting")
    bebop.disconnect()

Outdoor or large area demo of the direct flight commands on the bebop
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The second example program shows how to directly fly the bebop by controlling the yaw, pitch, roll, and
vertical movement parameters.  **Make sure you try this one in a large enough room!**
This code is provided in
`demoBebopDirectFlight.py <https://github.com/amymcgovern/pyparrot/blob/master/examples/demoBebopDirectFlight.py>`_
and is also shown below.


.. code-block:: python

    """
    Flies the bebop in a fairly wide arc.  You want to be sure you have room for this. (it is commented
    out but even what is here is still going to require a large space)

    Author: Amy McGovern
    """
    from pyparrot.Bebop import Bebop

    bebop = Bebop()

    print("connecting")
    success = bebop.connect(10)
    print(success)

    print("sleeping")
    bebop.smart_sleep(5)

    bebop.ask_for_state_update()

    bebop.safe_takeoff(10)

    print("Flying direct: going forward (positive pitch)")
    bebop.fly_direct(roll=0, pitch=50, yaw=0, vertical_movement=0, duration=1)

    print("Flying direct: yaw")
    bebop.fly_direct(roll=0, pitch=0, yaw=50, vertical_movement=0, duration=1)

    print("Flying direct: going backwards (negative pitch)")
    bebop.fly_direct(roll=0, pitch=-50, yaw=0, vertical_movement=0, duration=0.5)

    print("Flying direct: roll")
    bebop.fly_direct(roll=50, pitch=0, yaw=0, vertical_movement=0, duration=1)

    print("Flying direct: going up")
    bebop.fly_direct(roll=0, pitch=0, yaw=0, vertical_movement=50, duration=1)

    print("Turning relative")
    bebop.move_relative(0, 0, 0, math.radians(90))

    # this works but requires a larger test space than I currently have. Uncomment with care and test only in large spaces!
    #print("Flying direct: going around in a circle (yes you can mix roll, pitch, yaw in one command!)")
    #bebop.fly_direct(roll=25, pitch=0, yaw=50, vertical_movement=0, duration=5)

    bebop.smart_sleep(5)
    bebop.safe_land(10)

    print("DONE - disconnecting")
    bebop.disconnect()


Indoor demo of the direct flight commands on the bebop
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you couldn't run the outdoor or large space demo to test your bebop, this one is designed for a smaller space.
It simply takes off, turns, and lands. **Make sure you are still flying in a safe place!** This code is provided in
`demoBebopIndoors.py <https://github.com/amymcgovern/pyparrot/blob/master/examples/demoBebopIndoors.py>`_
and is also shown below.


.. code-block:: python

    """
    Demo the Bebop indoors (sets small speeds and then flies just a small amount)
    Note, the bebop will hurt your furniture if it hits it.  Even though this is a very small
    amount of flying, be sure you are doing this in an open area and are prepared to catch!

    Author: Amy McGovern
    """

    from pyparrot.Bebop import Bebop

    bebop = Bebop()

    print("connecting")
    success = bebop.connect(10)
    print(success)

    if (success):
        print("turning on the video")
        bebop.start_video_stream()

        print("sleeping")
        bebop.smart_sleep(2)

        bebop.ask_for_state_update()

        bebop.safe_takeoff(10)

        # set safe indoor parameters
        bebop.set_max_tilt(5)
        bebop.set_max_vertical_speed(1)

        # trying out the new hull protector parameters - set to 1 for a hull protection and 0 without protection
        bebop.set_hull_protection(1)

        print("Flying direct: Slow move for indoors")
        bebop.fly_direct(roll=0, pitch=20, yaw=0, vertical_movement=0, duration=2)

        bebop.smart_sleep(5)

        bebop.safe_land(10)

        print("DONE - disconnecting")
        bebop.stop_video_stream()
        bebop.smart_sleep(5)
        bebop.disconnect()