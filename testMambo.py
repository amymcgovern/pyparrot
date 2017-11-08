from Mambo import Mambo
import time

pigAddr = "e0:14:f4:20:3d:ce"
eagletAddr = "e0:14:d0:63:3d:d0"
owletAddr = "e0:14:0c:74:3d:fe"

# make my mambo object
mambo = Mambo(eagletAddr, use_wifi=True)
success = mambo.connect(num_retries=5)

mambo.ask_for_state_update()
mambo.smart_sleep(2)

if (success and False):
    mambo.takeoff()
    mambo.smart_sleep(5)
    mambo.land()
    mambo.smart_sleep(3)
    mambo.land()
    mambo.smart_sleep(3)
    mambo.disconnect()

print "DONE"