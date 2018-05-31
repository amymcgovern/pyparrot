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