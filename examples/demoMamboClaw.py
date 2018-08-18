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
