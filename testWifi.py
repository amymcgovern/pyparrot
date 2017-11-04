from networking.wifiConnection import WifiConnection
from Mambo import Mambo

mwifi = WifiConnection(drone_type="Mambo")
success = mwifi.connect(num_retries=5)
print success

pigAddr = "e0:14:f4:20:3d:ce"
eagletAddr = "e0:14:d0:63:3d:d0"
owletAddr = "e0:14:0c:74:3d:fe"

# make my mambo object
mambo = Mambo(pigAddr, use_wifi=True)


