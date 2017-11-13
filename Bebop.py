"""
Mambo class holds all of the methods needed to pilot the drone from python and to ask for sensor
data back from the drone

Author: Amy McGovern, dramymcgovern@gmail.com
"""
import time
from networking.wifiConnection import WifiConnection
from utils.colorPrint import color_print
from commandsandsensors.DroneCommandParser import DroneCommandParser
from commandsandsensors.DroneSensorParser import DroneSensorParser

class BebopSensors:
    def __init__(self):
        self.latitude = None
        self.longitude = None
        self.speed_x = None
        self.speed_y = None
        self.speed_z = None
        self.altitude = None
        self.roll = None
        self.tilt = None


    def update(self, sensor_name, sensor_value, sensor_enum):
        if (sensor_name == "PositionChanged_latitude"):
            self.latitude = sensor_value
        elif (sensor_name == "PositionChanged_longitude"):
            self.longitude = sensor_value
        elif (sensor_name == "SpeedChanged_speedX"):
            self.speed_x = sensor_value
        elif (sensor_name == "SpeedChanged_speedY"):
            self.speed_y = sensor_value
        elif (sensor_name == "SpeedChanged_speedZ"):
            self.speed_z = sensor_value
        elif (sensor_name == "AltitudeChanged_altitude"):
            self.altitude = sensor_value
        elif (sensor_name == "AttitudeChanged_roll"):
            self.roll = sensor_value
        elif (sensor_name == "Orientation_tilt"):
            self.tilt = sensor_value
        else:
            print("got a new sensor of ")
            print(sensor_name)
            print("and a new value of ")
            print(sensor_value)

class Bebop:
    def __init__(self):
        """
        Create a new Bebop object.  Assumes you have connected to the Bebop's wifi

        """
        self.drone_connection = WifiConnection(self, drone_type="Bebop")

        # intialize the command parser
        self.command_parser = DroneCommandParser()

        # initialize the sensors and the parser
        self.sensors = BebopSensors()
        self.sensor_parser = DroneSensorParser(drone_type="Bebop")


    def update_sensors(self, data_type, sequence_number, raw_data, ack):
        """
        Update the sensors (called via the wifi or ble connection)

        :param data: raw data packet that needs to be parsed
        :param ack: True if this packet needs to be ack'd and False otherwise
        """
        (sensor_name, sensor_value, sensor_enum, header_tuple) = self.sensor_parser.extract_sensor_values(raw_data)
        if (sensor_name is not None):
            self.sensors.update(sensor_name, sensor_value, sensor_enum)
            print(self.sensors)
        else:
            print("Need to figure out why this sensor is missing")


        if (ack):
            self.drone_connection.ack_packet(sequence_number)


    def connect(self, num_retries):
        """
        Connects to the drone and re-tries in case of failure the specified number of times.  Seamlessly
        connects to either wifi or BLE depending on how you initialized it

        :param: num_retries is the number of times to retry

        :return: True if it succeeds and False otherwise
        """

        # special case for when the user tries to do BLE when it isn't available
        if (self.drone_connection is None):
            return False

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
        command_tuple = self.command_parser.get_command_tuple("ardrone3", "Piloting", "TakeOff")
        self.drone_connection.send_noparam_command_packet_ack(command_tuple)


    def land(self):
        """
        Sends the land command to the mambo.  Gets the codes for it from the xml files.  Ensures the
        packet was received or sends it again up to a maximum number of times.

        :return: True if the command was sent and False otherwise
        """
        command_tuple = self.command_parser.get_command_tuple("ardrone3", "Piloting", "Landing")
        return self.drone_connection.send_noparam_command_packet_ack(command_tuple)


    def smart_sleep(self, timeout):
        """
        Don't call time.sleep directly as it will mess up BLE and miss WIFI packets!  Use this
        which handles packets received while sleeping

        :param timeout: number of seconds to sleep
        """
        self.drone_connection.smart_sleep(timeout)

