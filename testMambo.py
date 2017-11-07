from Mambo import Mambo
import time

pigAddr = "e0:14:f4:20:3d:ce"
eagletAddr = "e0:14:d0:63:3d:d0"
owletAddr = "e0:14:0c:74:3d:fe"

# make my mambo object
mambo = Mambo(pigAddr, use_wifi=False)
success = mambo.connect(num_retries=5)

if (success):
    mambo.takeoff()
    mambo.smart_sleep(5)
    mambo.land()
    mambo.smart_sleep(3)
    mambo.land()
    mambo.smart_sleep(3)
    mambo.disconnect()

