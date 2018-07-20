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
