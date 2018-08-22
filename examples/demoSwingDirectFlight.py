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
