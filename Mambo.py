"""
Mambo class holds all of the methods needed to pilot the drone from python and to ask for sensor
data back from the drone

Author: Amy McGovern, dramymcgovern@gmail.com
"""
import time
from networking.wifiConnection import WifiConnection
from networking.bleConnection import BLEConnection
from utils.colorPrint import color_print
from commandsandsensors.DroneCommandParser import DroneCommandParser
from commandsandsensors.DroneSensorParser import DroneSensorParser

class MamboSensors:
    """
    Store the mambo's last known sensor values
    """

    def __init__(self):

        # default to full battery
        self.battery = 100

        # drone on the ground
        self.flying_state = "landed"

        self.unknown_sensors = dict()

        self.gun_id = 0
        self.gun_state = None

        self.claw_id = 0
        self.claw_state = None

        # new SDK sends speed, altitude, and quaternions
        self.speed_x = 0
        self.speed_y = 0
        self.speed_z = 0
        self.speed_ts = 0

        # these are only available on wifi
        self.altitude = None
        self.altitude_ts = None

        self.quaternion_w = None
        self.quaternion_x = None
        self.quaternion_y = None
        self.quaternion_z = None
        self.quaternion_ts = None

    def update(self, name, value, sensor_enum):
        """
        Update the sensor

        :param name: name of the sensor to update
        :param value: new value for the sensor
        :param sensor_enum: enum list for the sensors that use enums so that we can translate from numbers to strings
        :return:
        """
        if (name, "enum") in sensor_enum:
            # grab the string value
            if (value > len(sensor_enum[(name, "enum")])):
                value = "UNKNOWN_ENUM_VALUE"
            else:
                enum_value = sensor_enum[(name, "enum")][value]
                value = enum_value

        # add it to the sensors
        if (name == "BatteryStateChanged_battery_percent"):
            self.battery = value
        elif (name == "FlyingStateChanged_state"):
            self.flying_state = value
        elif (name == "ClawState_id"):
            self.claw_id = value
        elif (name == "ClawState_state"):
            self.claw_state = value
        elif (name == "GunState_id"):
            self.gun_id = value
        elif (name == "GunState_state"):
            self.gun_state = value
        elif (name == "DroneSpeed_speed_x"):
            self.speed_x = value
        elif (name == "DroneSpeed_speed_y"):
            self.speed_y = value
        elif (name == "DroneSpeed_speed_z"):
            self.speed_z = value
        elif (name == "DroneSpeed_ts"):
            self.speed_ts = value
        elif (name == "DroneAltitude_altitude"):
            self.altitude = value
        elif (name == "DroneAltitude_altitude_ts"):
            self.altitude_ts = value
        elif (name == "DroneQuaternion_q_w"):
            self.quaternion_w = value
        elif (name == "DroneQuaternion_q_x"):
            self.quaternion_x = value
        elif (name == "DroneQuaternion_q_y"):
            self.quaternion_y = value
        elif (name == "DroneQuaternion_q_z"):
            self.quaternion_z = value
        elif (name == "DroneQuaternion_tz"):
            self.quaternion_ts = value
        else:
            #print "new sensor - add me to the struct but saving in the dict for now"
            self.unknown_sensors[name] = value

    def __str__(self):
        """
        Make a nicely printed struct for debugging

        :return: string for print calls
        """
        my_str = "mambo state: battery %d, " % self.battery
        my_str += "flying state is %s, " % self.flying_state
        my_str += "speed (x, y, z) and ts is (%f, %f, %f) at %f " % (self.speed_x, self.speed_y, self.speed_z, self.speed_ts)
        my_str += "altitude (m) %f and ts is %f " % (self.altitude, self.altitude_ts)
        my_str += "quaternion (w, x, y, z) and ts is (%f, %f, %f, %f) at %f " % (
            self.quaternion_w, self.quaternion_x, self.quaternion_y, self.quaternion_z, self.quaternion_ts)
        my_str += "gun id: %d, state %s, " % (self.gun_id, self.gun_state)
        my_str += "claw id: %d, state %s, " % (self.claw_id, self.claw_state)
        my_str += "unknown sensors: %s," % self.unknown_sensors
        return my_str


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
            self.drone_connection = BLEConnection(address, self)

        # intialize the command parser
        self.command_parser = DroneCommandParser()

        # initialize the sensors and the parser
        self.sensors = MamboSensors()
        self.sensor_parser = DroneSensorParser()


    def update_sensors(self, data, ack):
        """
        Update the sensors (called via the wifi or ble connection)

        :param data: raw data packet that needs to be parsed
        :param ack: True if this packet needs to be ack'd and False otherwise
        """
        (sensor_name, sensor_value, sensor_enum, header_tuple) = self.sensor_parser.extract_sensor_values(data)

        if (ack):
            self.drone_connection.ack_packet(header_tuple[1])

        self.sensors.update(sensor_name, sensor_value, sensor_enum)


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
        command_tuple = self.command_parser.get_command_tuple("Piloting", "TakeOff")
        self.drone_connection.send_noparam_command_packet_ack(command_tuple)


    def safe_takeoff(self, timeout):
        """
        Sends commands to takeoff until the mambo reports it is taking off

        :param timeout: quit trying to takeoff if it takes more than timeout seconds
        """

        start_time = time.time()
        # take off until it really listens
        while (self.sensors.flying_state != "takingoff" and (time.time() - start_time < timeout)):
            self.smart_sleep(1)
            success = self.takeoff()

        # now wait until it finishes takeoff before returning
        while ((self.sensors.flying_state != "flying" or self.sensors.flying_state != "hovering") and
                   (time.time() - start_time < timeout)):
            self.smart_sleep(1)

    def land(self):
        """
        Sends the land command to the mambo.  Gets the codes for it from the xml files.  Ensures the
        packet was received or sends it again up to a maximum number of times.

        :return: True if the command was sent and False otherwise
        """
        command_tuple = self.command_parser.get_command_tuple("Piloting", "Landing")
        return self.drone_connection.send_noparam_command_packet_ack(command_tuple)

    def safe_land(self):
        """
        Ensure the mambo lands by sending the command until it shows landed on sensors
        """

        while (self.sensors.flying_state != "landed"):
            color_print("trying to land", "INFO")
            self.smart_sleep(1)
            success = self.land()

    def smart_sleep(self, timeout):
        """
        Don't call time.sleep directly as it will mess up BLE and miss WIFI packets!  Use this
        which handles packets received while sleeping

        :param timeout: number of seconds to sleep
        """
        self.drone_connection.smart_sleep(timeout)

    def hover(self):
        """
        Sends the command execute a flat trim to the mambo.  This is basically a hover command.
        Gets the codes for it from the xml files. Ensures the
        packet was received or sends it again up to a maximum number of times.

        :return: True if the command was sent and False otherwise
        """
        command_tuple = self.command_parser.get_command_tuple("Piloting", "FlatTrim")
        # print command_tuple
        return self.drone_connection.send_noparam_command_packet_ack(command_tuple)

    def flip(self, direction):
        """
        Sends the flip command to the mambo.  Gets the codes for it from the xml files. Ensures the
        packet was received or sends it again up to a maximum number of times.
        Valid directions to flip are: front, back, right, left

        :return: True if the command was sent and False otherwise
        """
        if (direction not in ("front", "back", "right", "left")):
            print "Error: %s is not a valid direction.  Must be one of %s" % direction, "front, back, right, or left"
            print "Ignoring command and returning"
            return

        (command_tuple, enum_tuple) = self.command_parser.get_command_tuple_with_enum("Animations", "Flip", direction)
        # print command_tuple
        # print enum_tuple

        return self.drone_connection.send_enum_command_packet_ack(command_tuple, enum_tuple)

    def turn_degrees(self, degrees):
        """
        Turn the mambo the specified number of degrees (-180, 180)

        This is called cap in the xml but it means degrees per
        http://forum.developer.parrot.com/t/what-does-cap-stand-for/6213/2

        :param degrees: degrees to turn (-180 to 180)
        :return: True if the command was sent and False otherwise
        """
        command_tuple = self.command_parser.get_command_tuple("Animations", "Cap")
        return self.drone_connection.send_turn_command(command_tuple, degrees)

    def turn_on_auto_takeoff(self):
        """
        Turn on the auto take off (throw mode)
        :return: True if the command was sent and False otherwise
        """
        command_tuple = self.command_parser.get_command_tuple("Piloting", "AutoTakeOffMode")

        return self.drone_connection.send_auto_takeoff_command(command_tuple)


    def take_picture(self):
        """
        Ask the drone to take a picture

        :return: True if the command was sent and False otherwise
        """
        command_tuple = self.command_parser.get_command_tuple("MediaRecord", "PictureV2")
        return self.drone_connection.send_noparam_command_packet_ack(command_tuple)

    def ask_for_state_update(self):
        """
        Ask for a full state update (likely this should never be used but it can be called if you want to see
        everything the mambo is storing)

        :return: nothing but it will eventually fill the MamboSensors with all of the state variables as they arrive
        """
        command_tuple = self.command_parser.get_command_tuple("Common", "AllStates")
        return self.drone_connection.send_noparam_command_packet_ack(command_tuple)

    def _ensure_fly_command_in_range(self, value):
        """
        Ensure the fly direct commands are in range

        :param value: the value sent by the user
        :return: a value in the range -100 to 100
        """
        if (value < -100):
            return -100
        elif (value > 100):
            return 100
        else:
            return value

    def fly_direct(self, roll, pitch, yaw, vertical_movement, duration):
        """
        Direct fly commands using PCMD.  Each argument ranges from -100 to 100.  Numbers outside that are clipped
        to that range.

        Note that the xml refers to gaz, which is apparently french for vertical movements:
        http://forum.developer.parrot.com/t/terminology-of-gaz/3146

        :param roll:
        :param pitch:
        :param yaw:
        :param vertical_movement:
        :return:
        """

        my_roll = self._ensure_fly_command_in_range(roll)
        my_pitch = self._ensure_fly_command_in_range(pitch)
        my_yaw = self._ensure_fly_command_in_range(yaw)
        my_vertical = self._ensure_fly_command_in_range(vertical_movement)
        command_tuple = self.command_parser.get_command_tuple("Piloting", "PCMD")

        self.drone_connection.send_pcmd_command(my_roll, my_pitch, my_yaw, my_vertical, duration)


    def open_claw(self):
        """
        Open the claw
        :return: nothing
        """
        # print "open claw"
        (command_tuple, enum_tuple) = self.command_parser.get_command_tuple_with_enum("UsbAccessory", "ClawControl", "OPEN")
        # print command_tuple
        # print enum_tuple

        return self.drone_connection.send_enum_command_packet_ack(command_tuple, enum_tuple, self.sensors.claw_id)

    def close_claw(self):
        """
        Open the claw
        :return: nothing
        """
        # print "close claw"
        (command_tuple, enum_tuple) = self.command_parser.get_command_tuple_with_enum("UsbAccessory", "ClawControl", "CLOSE")
        # print command_tuple
        # print enum_tuple

        return self.drone_connection.send_enum_command_packet_ack(command_tuple, enum_tuple, self.sensors.claw_id)

    def fire_gun(self):
        """
        Fire the gun (assumes it is attached)

        :return: nothing
        """
        # print "firing gun"
        (command_tuple, enum_tuple) = self.command_parser.get_command_tuple_with_enum("UsbAccessory", "GunControl", "FIRE")
        # print command_tuple
        # print enum_tuple

        return self.drone_connection.send_enum_command_packet_ack(command_tuple, enum_tuple, self.sensors.gun_id)

