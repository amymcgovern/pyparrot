from Bebop import Bebop

bebop = Bebop()

print("connecting")
success = bebop.connect(10)
print(success)

print("sleeping")
bebop.smart_sleep(5)

bebop.ask_for_state_update()

#TODO: Check for flying state of emergency

#bebop.takeoff()
bebop.safe_takeoff(10)

#bebop.fly_direct(roll=0, pitch=0, yaw=0, vertical_movement=25, duration=1)

# bebop.fly_relative(change_x=0.5, change_y=0, change_z=0, change_angle=0, wait_for_end=True)

if (False):
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

if (False):
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

#print("Flying direct: going around in a circle (yes you can mix roll, pitch, yaw in one command!)")
#bebop.fly_direct(roll=25, pitch=0, yaw=50, vertical_movement=0, duration=5)

bebop.smart_sleep(5)
bebop.safe_land(10)

#bebop.land()
#bebop.smart_sleep(5)

#bebop.move_camera(5, 5, wait_for_end=True)

print("DONE - disconnecting")
bebop.disconnect()