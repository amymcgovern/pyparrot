from Bebop import Bebop

bebop = Bebop()

print("connecting")
success = bebop.connect(10)
print(success)

print("sleeping")
bebop.smart_sleep(5)

bebop.takeoff()
bebop.smart_sleep(5)
bebop.land()

print("DONE - disconnecting")
bebop.disconnect()