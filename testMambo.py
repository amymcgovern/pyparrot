from Mambo import Mambo
import time

pigAddr = "e0:14:f4:20:3d:ce"
eagletAddr = "e0:14:d0:63:3d:d0"
owletAddr = "e0:14:0c:74:3d:fe"

# make my mambo object
mambo = Mambo(eagletAddr, use_wifi=True)
success = mambo.connect(num_retries=5)

if (success and False):
    mambo.ask_for_state_update()
    mambo.smart_sleep(2)
    mambo.ask_for_state_update()
    mambo.smart_sleep(2)
    mambo.ask_for_state_update()
    mambo.smart_sleep(2)

if (success):
    mambo.safe_takeoff(5)

    #mambo.fly_direct(roll=0, pitch=0,yaw=25,vertical_movement=0,duration=1)
    #mambo.smart_sleep(2)

    mambo.flip(direction="front")
    mambo.smart_sleep(2)

    #mambo.smart_sleep(5)
    mambo.safe_land(5)
    mambo.smart_sleep(3)
    #mambo.land()
    #mambo.smart_sleep(3)
    #mambo.disconnect()

mambo.disconnect()
print("DONE")