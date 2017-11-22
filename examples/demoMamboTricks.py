"""
Demo the trick flying for the python interface
"""

from Mambo import Mambo

# you will need to change this to the address of YOUR mambo
mamboAddr = "e0:14:d0:63:3d:d0"

# make my mambo object
# remember to set True/False for the wifi depending on if you are using the wifi or the BLE to connect
mambo = Mambo(mamboAddr, use_wifi=True)

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

print("Flying direct: going up")
mambo.fly_direct(roll=0, pitch=0, yaw=0, vertical_movement=50, duration=1)

print("flip left")
success = mambo.flip(direction="left")
print("mambo flip result %s" % success)
mambo.smart_sleep(5)

print("flip right")
success = mambo.flip(direction="right")
print("mambo flip result %s" % success)
mambo.smart_sleep(5)

print("flip front")
success = mambo.flip(direction="front")
print("mambo flip result %s" % success)
mambo.smart_sleep(5)

print("flip back")
success = mambo.flip(direction="back")
print("mambo flip result %s" % success)
mambo.smart_sleep(5)

print("landing")
mambo.safe_land(5)
mambo.smart_sleep(5)

print("disconnect")
mambo.disconnect()

