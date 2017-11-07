"""
Demo the claw for the python interface
"""

from Mambo import Mambo

# you will need to change this to the address of YOUR mambo
mamboAddr = "e0:14:d0:63:3d:d0"

# make my mambo object
# remember to set True/False for the wifi depending on if you are using the wifi or the BLE to connect
mambo = Mambo(mamboAddr, use_wifi=False)

print "trying to connect"
success = mambo.connect(num_retries=3)
print "connected: %s" % success

# get the state information
print "sleeping"
mambo.smart_sleep(2)
mambo.ask_for_state_update()
mambo.smart_sleep(2)

print "taking off!"
mambo.safe_takeoff(5)

print "open and close the claw"
mambo.open_claw()
# you have to sleep to let the claw open (it needs time to do it)
mambo.smart_sleep(5)

mambo.close_claw()
# you have to sleep to let the claw close (it needs time to do it)
mambo.smart_sleep(5)

print "landing"
mambo.safe_land()
mambo.smart_sleep(5)

print "disconnect"
mambo.disconnect()

