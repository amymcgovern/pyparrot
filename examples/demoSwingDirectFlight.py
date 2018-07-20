"""
Demo the direct flying for the python interface

Author: Victor804
"""

from pyparrot.Minidrone import Swing

# you will need to change this to the address of YOUR mambo
swingAddr = "e0:14:04:a7:3d:cb"

# make my mambo object
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

    print("Flying direct: going forward (positive pitch)")
    swing.fly_direct(roll=0, pitch=50, yaw=0, vertical_movement=0, duration=1)

    print("Showing turning (in place) using turn_degrees")
    swing.turn_degrees(90)
    swing.smart_sleep(2)
    swing.turn_degrees(-90)
    swing.smart_sleep(2)

    print("Flying direct: yaw")
    swing.fly_direct(roll=0, pitch=0, yaw=50, vertical_movement=0, duration=1)

    print("Flying direct: going backwards (negative pitch)")
    swing.fly_direct(roll=0, pitch=-50, yaw=0, vertical_movement=0, duration=0.5)

    print("Flying direct: roll")
    swing.fly_direct(roll=50, pitch=0, yaw=0, vertical_movement=0, duration=1)

    print("Flying direct: going up")
    swing.fly_direct(roll=0, pitch=0, yaw=0, vertical_movement=50, duration=1)

    print("Flying direct: going around in a circle (yes you can mix roll, pitch, yaw in one command!)")
    swing.fly_direct(roll=25, pitch=0, yaw=50, vertical_movement=0, duration=3)

    print("landing")
    swing.safe_land(5)
    swing.smart_sleep(5)

    print("disconnect")
    swing.disconnect()
