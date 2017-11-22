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
        self.sensors = dict()

    def update(self, sensor_name, sensor_value, sensor_enum):
        if (sensor_name is None):
            print("Error empty sensor")
            return


        if (sensor_name, "enum") in sensor_enum:
            # grab the string value
            if (sensor_value > len(sensor_enum[(sensor_name, "enum")])):
                value = "UNKNOWN_ENUM_VALUE"
            else:
                enum_value = sensor_enum[(sensor_name, "enum")][sensor_value]
                value = enum_value

            self.sensors[sensor_name] = value

        else:
            # regular sensor
            self.sensors[sensor_name] = sensor_value

    def __str__(self):
        str = "Bebop sensors: %s" % self.sensors
        return str

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


    def update_sensors(self, data_type, buffer_id, sequence_number, raw_data, ack):
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
            print("data type %d buffer id %d sequence number %d" % (data_type, buffer_id, sequence_number))
            print("Need to figure out why this sensor is missing")


        if (ack):
            self.drone_connection.ack_packet(buffer_id, sequence_number)


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

    def ask_for_state_update(self):
        """
        Ask for a full state update (likely this should never be used but it can be called if you want to see
        everything the bebop is storing)

        :return: nothing but it will eventually fill the sensors with all of the state variables as they arrive
        """
        command_tuple = self.command_parser.get_command_tuple("common", "Common", "AllStates")
        return self.drone_connection.send_noparam_command_packet_ack(command_tuple)


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

