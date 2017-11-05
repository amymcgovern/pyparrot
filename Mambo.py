"""
Mambo class holds all of the methods needed to pilot the drone from python and to ask for sensor
data back from the drone

Author: Amy McGovern, dramymcgovern@gmail.com
"""
import time
from networking.wifiConnection import WifiConnection
from networking.bleConnection import BLEConnection
from utils.colorPrint import color_print
from commands.DroneCommands import DroneCommands


class Mambo:
    def __init__(self, address, use_wifi=False):
        """
        Initialize with its BLE address - if you don't know the address, call findMambo
        and that will discover it for you.

        You can also connect to the wifi on the FPV camera.  Do not use this if the camera is not connected.  Also,
        ensure you have connected your machine to the wifi on the camera before attempting this or it will not work.

        :param address: unique address for this mambo
        :param use_wifi: set to True to connect with wifi as well as the BLE
        """
        self.address = address
        if (use_wifi):
            self.drone_connection = WifiConnection(drone_type="Mambo")
        else:
            self.drone_connection = BLEConnection(address)

        # intialize the command parser
        self.drone_commands = DroneCommands()


    def connect(self, num_retries):
        """
        Connects to the drone and re-tries in case of failure the specified number of times.  Seamlessly
        connects to either wifi or BLE depending on how you initialized it

        :param: num_retries is the number of times to retry

        :return: True if it succeeds and False otherwise
        """

        connected = self.drone_connection.connect(num_retries)
        return connected


    def disconnect(self):
        """
        Disconnect the BLE connection.  Always call this at the end of your programs to
        cleanly disconnect.

        :return: void
        """
        self.drone_connection.disconnect()


    def takeoff(self):
        """
        Sends the takeoff command to the mambo.  Gets the codes for it from the xml files.  Ensures the
        packet was received or sends it again up to a maximum number of times.

        :return: True if the command was sent and False otherwise
        """
        command_tuple = self.drone_commands.get_command_tuple("Piloting", "TakeOff")
        self.drone_connection.send_noparam_command_packet_ack(command_tuple)


    def land(self):
        """
        Sends the land command to the mambo.  Gets the codes for it from the xml files.  Ensures the
        packet was received or sends it again up to a maximum number of times.

        :return: True if the command was sent and False otherwise
        """
        command_tuple = self.drone_commands.get_command_tuple("Piloting", "Landing")
        return self.drone_connection.send_noparam_command_packet_ack(command_tuple)

    def smart_sleep(self, timeout):
        """
        Don't call time.sleep directly as it will mess up BLE and miss WIFI packets!  Use this
        which handles packets received while sleeping

        :param timeout: number of seconds to sleep
        """
        self.drone_connection.smart_sleep(timeout)