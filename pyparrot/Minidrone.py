"""
Mambo class holds all of the methods needed to pilot the drone from python and to ask for sensor
data back from the drone

Author: Amy McGovern, dramymcgovern@gmail.com
Author: Alexander Zach, https://github.com/alex-zach, groundcam support
Author: Valentin Benke, https://github.com/Vabe7, groundcam support
"""
import time
from pyparrot.networking.wifiConnection import WifiConnection
try:
    from pyparrot.networking.bleConnection import BLEConnection
    BLEAvailable = True
except:
    BLEAvailable = False
from pyparrot.utils.colorPrint import color_print
from pyparrot.commandsandsensors.DroneCommandParser import DroneCommandParser
from pyparrot.commandsandsensors.DroneSensorParser import DroneSensorParser
import math
from os.path import join
import inspect

#Groundcam Imports
from ftplib import FTP
import tempfile
try:
    import cv2
    OpenCVAvailable = True
    print("OpenCVAvailable is %s" % OpenCVAvailable)
except:
    OpenCVAvailable = False
    print("OpenCVAvailable is %s" % OpenCVAvailable)

class MinidroneSensors:
    """
    Store the minidrone's last known sensor values
    """

    def __init__(self):

        # default to full battery
        self.battery = 100

        # drone on the ground
        self.flying_state = "landed"

        # dictionary for extra sensors
        self.sensors_dict = dict()

        self.gun_id = 0
        self.gun_state = None

        self.claw_id = 0
        self.claw_state = None

        self.flying_mode = "quadricopter"
        self.plane_gear_box = "gear_1"

        # new SDK sends speed, altitude, and quaternions
        self.speed_x = 0
        self.speed_y = 0
        self.speed_z = 0
        self.speed_ts = 0

        # these are only available on wifi
        self.altitude = -1
        self.altitude_ts = 0

        self.quaternion_w = 0
        self.quaternion_x = 0
        self.quaternion_y = 0
        self.quaternion_z = 0
        self.quaternion_ts = -1

        # this is optionally set elsewhere
        self.user_callback_function = None

    def set_user_callback_function(self, function, args):
        """
        Sets the user callback function (called everytime the sensors are updated)

        :param function: name of the user callback function
        :param args: arguments (tuple) to the function
        :return:
        """
        self.user_callback_function = function
        self.user_callback_function_args = args

    def update(self, name, value, sensor_enum):
        """
        Update the sensor

        :param name: name of the sensor to update
        :param value: new value for the sensor
        :param sensor_enum: enum list for the sensors that use enums so that we can translate from numbers to strings
        :return:
        """
        #print("updating sensor %s" % name)
        #print(value)
        if (name is None):
            print("Error empty sensor")
            return


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
        elif (name == "DroneAltitude_ts"):
            self.altitude_ts = value
        elif (name == "DroneQuaternion_q_w"):
            self.quaternion_w = value
        elif (name == "DroneQuaternion_q_x"):
            self.quaternion_x = value
        elif (name == "DroneQuaternion_q_y"):
            self.quaternion_y = value
        elif (name == "DroneQuaternion_q_z"):
            self.quaternion_z = value
        elif (name == "DroneQuaternion_ts"):
            self.quaternion_ts = value
        elif (name == "FlyingModeChanged_mode"):
            self.flying_mode = value
        elif (name == "PlaneGearBoxChanged_state"):
            self.plane_gear_box = value
        else:
            #print "new sensor - add me to the struct but saving in the dict for now"
            self.sensors_dict[name] = value

        # call the user callback if it isn't None
        if (self.user_callback_function is not None):
            self.user_callback_function(self.user_callback_function_args)

    def get_estimated_z_orientation(self):
        """
        Uses the quaternions to return an estimated orientation

        Learn more about unit quaternions here:

        https://en.wikipedia.org/wiki/Quaternions_and_spatial_rotation

        NOTE: This is not a real compass heading.  0 degrees is where you are facing when
        the mambo turns on!

        :return:
        """

        (X, Y, Z) = self.quaternion_to_euler_angle(self.quaternion_w, self.quaternion_x,
                                                   self.quaternion_y, self.quaternion_z)
        return Z

    def quaternion_to_euler_angle(self, w, x, y, z):
        """
        This code is directly from:

        https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles

        :param x:
        :param y:
        :param z:
        :return:
        """
        ysqr = y * y

        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + ysqr)
        X = math.degrees(math.atan2(t0, t1))

        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        Y = math.degrees(math.asin(t2))

        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (ysqr + z * z)
        Z = math.degrees(math.atan2(t3, t4))

        return X, Y, Z

    def __str__(self):
        """
        Make a nicely printed struct for debugging

        :return: string for print calls
        """
        my_str = "mambo state: battery %d, " % self.battery
        my_str += "flying state is %s, " % self.flying_state
        my_str += "speed (x, y, z) and ts is (%f, %f, %f) at %f " % (self.speed_x, self.speed_y, self.speed_z, self.speed_ts)
        if (self.altitude_ts > -1):
            my_str += "altitude (m) %f and ts is %f " % (self.altitude, self.altitude_ts)

        if (self.quaternion_ts > -1):
            my_str += "quaternion (w, x, y, z) and ts is (%f, %f, %f, %f) at %f " % (
                self.quaternion_w, self.quaternion_x, self.quaternion_y, self.quaternion_z, self.quaternion_ts)
        my_str += "gun id: %d, state %s, " % (self.gun_id, self.gun_state)
        my_str += "claw id: %d, state %s, " % (self.claw_id, self.claw_state)
        my_str += "extra sensors: %s," % self.sensors_dict
        return my_str



class MamboGroundcam:
    def __init__(self):
        """
        Initialises the FTP-Session for the picture-download.
        Only works with WiFi.
        """
        self.MEDIA_PATH = '/internal_000/mambo/media'  # Filepath on the Mambo
        # groundcam remains broken on 3.0.26 and now it times out
        #try:
        #    self.ftp = FTP('192.168.99.3')  # IP-Address of the drone itself
        #    login = self.ftp.login()
        #    print("FTP login success is %s" % login)
        #except:
        print("ERROR: ftp login is disabled by parrot firmware 3.0.25 and 26.  Groundcam will not work.")
        self.ftp = None

        # get the path for the config files
        fullPath = inspect.getfile(Mambo)
        shortPathIndex = fullPath.rfind("/")
        if (shortPathIndex == -1):
            # handle Windows paths
            shortPathIndex = fullPath.rfind("\\")
        print(shortPathIndex)
        shortPath = fullPath[0:shortPathIndex]
        self.imagePath = join(shortPath, "images")
        self.storageFile = join(self.imagePath, "groundcam.jpg")
        print(self.storageFile)
        #self.storageFile = tempfile.NamedTemporaryFile()

    def _close(self):
        if (self.ftp is not None):
            self.ftp.close()

    def get_groundcam_pictures_names(self):
        """
        Retruns a list with the names of the pictures stored on the Mambo.
        :return The list as an array, if there isn't any file, the array is empty.
        """
        if (self.ftp is None):
            return list()
        else:
            self.ftp.cwd(self.MEDIA_PATH)
            list = self.ftp.nlst()
            list = sorted(list)
            return list

    def get_groundcam_picture(self, filename, cv2_flag):
        """
        Downloads the specified picture from the Mambo and stores it into a tempfile.

        :param filename: the name of the file which should be downloaded ON THE MAMBO.
        :param cv2_flag: if true this function will return a cv2 image object, if false the name of the temporary file will be returned
        :return False if there was an error during download, if cv2 is True a cv2 frame or it just returns the file name of the temporary file
        """
        # handle the broken firmware upgrade
        if (self.ftp is None):
            return False

        # otherwise return the photos
        self.ftp.cwd(self.MEDIA_PATH)
        try:
            self.ftp.retrbinary('RETR ' + filename, open(self.storageFile, "wb").write) #download
            if cv2_flag and OpenCVAvailable:
                img = cv2.imread(self.storageFile)
                return img
            else:
                return filename
        except Exception as e:
            print(e)
            return False

    def _delete_file(self, filename):
        '''
        Deletes a file on the drone
        :param filename: Filename of the file you wnat to delete
        '''
        if (self.ftp is not None):
            self.ftp.delete(filename)


class Minidrone:
    def __init__(self, address="", use_wifi=False):
        """
        If you need BLE: Initialize with its BLE address - if you don't know the address, call findMambo
        and that will discover it for you.
        You can also connect to the wifi on the FPV camera.  Do not use this if the camera is not connected.  Also,
        ensure you have connected your machine to the wifi on the camera before attempting this or it will not work.
        :param address: unique address for this mambo (can be ignored if you are using wifi)
        :param use_wifi: set to True to connect with wifi instead of BLE
        """
        self.address = address
        self.use_wifi = use_wifi
        self.groundcam = None
        if (use_wifi):
            self.drone_connection = WifiConnection(self, drone_type="Mambo")
            # initialize groundcam
            self.groundcam = MamboGroundcam()
        else:
            if (BLEAvailable):
                self.drone_connection = BLEConnection(address, self)
            else:
                self.drone_connection = None
                color_print("ERROR: you are trying to use a BLE connection on a system that doesn't have BLE installed.", "ERROR")
                return

        # intialize the command parser
        self.command_parser = DroneCommandParser()

        # initialize the sensors and the parser
        self.sensors = MinidroneSensors()
        self.sensor_parser = DroneSensorParser(drone_type="Minidrone")


    def set_user_sensor_callback(self, function, args):
        """
        Set the (optional) user callback function for sensors.  Every time a sensor
        is updated, it calls this function.

        :param function: name of the function
        :param args: tuple of arguments to the function
        :return: nothing
        """
        self.sensors.set_user_callback_function(function, args)

    def update_sensors(self, data_type, buffer_id, sequence_number, raw_data, ack):
        """
        Update the sensors (called via the wifi or ble connection)

        :param data: raw data packet that needs to be parsed
        :param ack: True if this packet needs to be ack'd and False otherwise
        """

        sensor_list = self.sensor_parser.extract_sensor_values(raw_data)
        if (sensor_list is not None):
            for sensor in sensor_list:
                (sensor_name, sensor_value, sensor_enum, header_tuple) = sensor
                if (sensor_name is not None):
                    self.sensors.update(sensor_name, sensor_value, sensor_enum)
                    # print(self.sensors)
                else:
                    color_print(
                        "data type %d buffer id %d sequence number %d" % (data_type, buffer_id, sequence_number),
                        "WARN")
                    color_print("This sensor is missing (likely because we don't need it)", "WARN")

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


    def takeoff(self):
        """
        Sends the takeoff command to the mambo.  Gets the codes for it from the xml files.  Ensures the
        packet was received or sends it again up to a maximum number of times.

        :return: True if the command was sent and False otherwise
        """
        command_tuple = self.command_parser.get_command_tuple("minidrone", "Piloting", "TakeOff")
        return self.drone_connection.send_noparam_command_packet_ack(command_tuple)


    def safe_takeoff(self, timeout):
        """
        Sends commands to takeoff until the mambo reports it is taking off

        :param timeout: quit trying to takeoff if it takes more than timeout seconds
        """

        start_time = time.time()
        # take off until it really listens
        while (self.sensors.flying_state != "takingoff" and (time.time() - start_time < timeout)):
            if (self.sensors.flying_state == "emergency"):
                return
            success = self.takeoff()
            self.smart_sleep(1)

        # now wait until it finishes takeoff before returning
        while ((self.sensors.flying_state not in ("flying", "hovering") and
                   (time.time() - start_time < timeout))):
            if (self.sensors.flying_state == "emergency"):
                return
            self.smart_sleep(1)

    def land(self):
        """
        Sends the land command to the mambo.  Gets the codes for it from the xml files.  Ensures the
        packet was received or sends it again up to a maximum number of times.

        :return: True if the command was sent and False otherwise
        """
        command_tuple = self.command_parser.get_command_tuple("minidrone", "Piloting", "Landing")
        return self.drone_connection.send_noparam_command_packet_ack(command_tuple)

    def is_landed(self):
        """
        Returns true if it is landed or emergency and False otherwise
        :return:
        """
        if (self.sensors.flying_state in ("landed", "emergency")):
            return True
        else:
            return False

    def safe_land(self, timeout):
        """
        Ensure the mambo lands by sending the command until it shows landed on sensors
        """
        start_time = time.time()

        while (self.sensors.flying_state not in ("landing", "landed") and (time.time() - start_time < timeout)):
            if (self.sensors.flying_state == "emergency"):
                return
            color_print("trying to land", "INFO")
            success = self.land()
            self.smart_sleep(1)

        while (self.sensors.flying_state != "landed" and (time.time() - start_time < timeout)):
            if (self.sensors.flying_state == "emergency"):
                return
            self.smart_sleep(1)


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
        command_tuple = self.command_parser.get_command_tuple("minidrone", "Piloting", "FlatTrim")
        # print command_tuple
        return self.drone_connection.send_noparam_command_packet_ack(command_tuple)

    def flip(self, direction):
        """
        Sends the flip command to the mambo.  Gets the codes for it from the xml files. Ensures the
        packet was received or sends it again up to a maximum number of times.
        Valid directions to flip are: front, back, right, left

        :return: True if the command was sent and False otherwise
        """
        fixed_direction = direction.lower()
        if (fixed_direction not in ("front", "back", "right", "left")):
            print("Error: %s is not a valid direction.  Must be one of %s" % direction, "front, back, right, or left")
            print("Ignoring command and returning")
            return

        (command_tuple, enum_tuple) = self.command_parser.get_command_tuple_with_enum("minidrone",
                                                                                      "Animations", "Flip", fixed_direction)
        # print command_tuple
        # print enum_tuple

        return self.drone_connection.send_enum_command_packet_ack(command_tuple, enum_tuple)

    def turn_degrees(self, degrees):
        """
        Turn the mambo the specified number of degrees (-180, 180).  Degrees must be an integere
        so it is cast to an integer here.  If you send it a float, it will be rounded according to
        the rules of int()

        This is called cap in the xml but it means degrees per
        http://forum.developer.parrot.com/t/what-does-cap-stand-for/6213/2

        :param degrees: degrees to turn (-180 to 180)
        :return: True if the command was sent and False otherwise
        """
        degrees = int(degrees)
        if (degrees > 180):
            degrees = 180
            print("Degrees too large: setting to 180")
        elif (degrees < -180):
            degrees = -180
            print("Degrees too large and negative: setting to -180")

        command_tuple = self.command_parser.get_command_tuple("minidrone", "Animations", "Cap")
        return self.drone_connection.send_turn_command(command_tuple, degrees)

    def turn_on_auto_takeoff(self):
        """
        Turn on the auto take off (throw mode)
        :return: True if the command was sent and False otherwise
        """
        command_tuple = self.command_parser.get_command_tuple("minidrone", "Piloting", "AutoTakeOffMode")

        return self.drone_connection.send_param_command_packet(command_tuple, param_tuple=[1], param_type_tuple=["u8"])


    def take_picture(self):
        """
        Ask the drone to take a picture also checks how many frames are on there, if there are ore than 35 it deletes one
        If connected via Wifi it
        If it is connected via WiFi it also deletes all frames on the Mambo once there are more than 35,
        since after there are 40 the next ones are ignored
        :return: True if the command was sent and False otherwise
        """
        if self.use_wifi:
            list = self.groundcam.get_groundcam_pictures_names()
            if len(list) > 35: #if more than 35 pictures on the Mambo delete all
                print("deleting")
                for file in list:
                    self.groundcam._delete_file(file)

        command_tuple = self.command_parser.get_command_tuple("minidrone", "MediaRecord", "PictureV2")
        return self.drone_connection.send_noparam_command_packet_ack(command_tuple)

    def ask_for_state_update(self):
        """
        Ask for a full state update (likely this should never be used but it can be called if you want to see
        everything the mambo is storing)

        :return: nothing but it will eventually fill the MamboSensors with all of the state variables as they arrive
        """
        command_tuple = self.command_parser.get_command_tuple("common", "Common", "AllStates")
        return self.drone_connection.send_noparam_command_packet_ack(command_tuple)

    def _ensure_fly_command_in_range(self, value):
        """
        Ensure the fly direct commands are in range and also ensures the values are integers (just rounds them)

        :param value: the value sent by the user
        :return: a value in the range -100 to 100
        """
        if (value < -100):
            return -100
        elif (value > 100):
            return 100
        else:
            return int(value)

    def fly_direct(self, roll, pitch, yaw, vertical_movement, duration=None):
        """
        Direct fly commands using PCMD.  Each argument ranges from -100 to 100.  Numbers outside that are clipped
        to that range.

        Note that the xml refers to gaz, which is apparently french for vertical movements:
        http://forum.developer.parrot.com/t/terminology-of-gaz/3146

        duration is optional: if you want it to fly for a specified period of time, set this to the number of
        seconds (fractions are fine) or use None to send the command once.  Note, if you do this, you will need
        an outside loop that sends lots of commands or your drone will not fly very far.  The command is not repeated
        inside the drone.  it executes once and goes back to hovering without new commands coming in.  But the option
        of zero duration allows for smoother flying if you want to do the control loop yourself.


        :param roll: roll speed in -100 to 100
        :param pitch: pitch speed in -100 to 100
        :param yaw: yaw speed in -100 to 100
        :param vertical_movement: vertical speed in -100 to 100
        :param duration: optional: seconds for a specified duration or None to send it once (see note above)
        :return:
        """

        my_roll = self._ensure_fly_command_in_range(roll)
        my_pitch = self._ensure_fly_command_in_range(pitch)
        my_yaw = self._ensure_fly_command_in_range(yaw)
        my_vertical = self._ensure_fly_command_in_range(vertical_movement)

        #print("roll is %d pitch is %d yaw is %d vertical is %d" % (my_roll, my_pitch, my_yaw, my_vertical))
        command_tuple = self.command_parser.get_command_tuple("minidrone", "Piloting", "PCMD")

        if (duration is None):
            self.drone_connection.send_single_pcmd_command(command_tuple, my_roll, my_pitch, my_yaw, my_vertical)
        else:
            self.drone_connection.send_pcmd_command(command_tuple, my_roll, my_pitch, my_yaw, my_vertical, duration)



    def open_claw(self):
        """
        Open the claw - note not supposed under wifi since the camera takes the place of the claw

        :return: True if the command was sent and False otherwise (can include errors or asking to do this using wifi)
        """
        # not supposed under wifi since the camera takes the place of the claw
        if (self.use_wifi):
            return False

        # print "open claw"
        (command_tuple, enum_tuple) = self.command_parser.get_command_tuple_with_enum("minidrone", "UsbAccessory", "ClawControl", "OPEN")
        # print command_tuple
        # print enum_tuple

        return self.drone_connection.send_enum_command_packet_ack(command_tuple, enum_tuple, self.sensors.claw_id)

    def close_claw(self):
        """
        Close the claw - note not supposed under wifi since the camera takes the place of the claw

        :return: True if the command was sent and False otherwise (can include errors or asking to do this using wifi)
        """

        # not supposed under wifi since the camera takes the place of the claw
        if (self.use_wifi):
            return False

        # print "close claw"
        (command_tuple, enum_tuple) = self.command_parser.get_command_tuple_with_enum("minidrone", "UsbAccessory", "ClawControl", "CLOSE")
        # print command_tuple
        # print enum_tuple

        return self.drone_connection.send_enum_command_packet_ack(command_tuple, enum_tuple, self.sensors.claw_id)


    def set_max_vertical_speed(self, value):
        """
        Sets the maximum vertical speed in m/s.  Unknown what the true maximum is but
        we do ensure you only set positive values.

        :param value: maximum speed
        :return: True if the command was sent and False otherwise
        """

        if (value < 0):
            print("Can't set a negative max vertical speed.  Setting to 1 m/s instead.")
            value = 1

        command_tuple = self.command_parser.get_command_tuple("minidrone", "SpeedSettings", "MaxVerticalSpeed")
        param_tuple = [value]
        param_type_tuple = ['float']
        return self.drone_connection.send_param_command_packet(command_tuple,param_tuple,param_type_tuple)

    def set_max_tilt(self, value):
        """
        Sets the maximum tilt in degrees.  Ensures you only set positive values.

        :param value: maximum tilt in degrees
        :return: True if the command was sent and False otherwise
        """

        if (value < 0):
            print("Can't set a negative max horizontal speed.  Setting to 1 m/s instead.")
            value = 1

        command_tuple = self.command_parser.get_command_tuple("minidrone", "PilotingSettings", "MaxTilt")
        param_tuple = [value]
        param_type_tuple = ['float']
        return self.drone_connection.send_param_command_packet(command_tuple,param_tuple,param_type_tuple)

    def emergency(self):
        """
        Sends the emergency command to the mambo.  Gets the codes for it from the xml files.  Ensures the
        packet was received or sends it again up to a maximum number of times.

        :return: True if the command was sent and False otherwise
        """
        command_tuple = self.command_parser.get_command_tuple("minidrone", "Piloting", "Emergency")
        self.drone_connection.send_noparam_command_packet_ack(command_tuple)


    def safe_emergency(self, timeout):
        """
        Sends emergency stop command  until the Mambo reports it is not flying anymore

        :param timeout: quit trying to emergency stop if it takes more than timeout seconds
        """

        start_time = time.time()
        # send emergency until it really listens
        while ((self.sensors.flying_state in ("flying", "hovering")) and (time.time() - start_time < timeout)):
            success = self.emergency()
            self.smart_sleep(1)

        # now wait until it touches ground before returning
        while ((self.sensors.flying_state != "landed") and (time.time() - start_time < timeout)):
            self.smart_sleep(1)

    def flat_trim(self):
        """
        Sends the flat_trim command to the mambo. Gets the codes for it from the xml files.
        """
        command_tuple = self.command_parser.get_command_tuple("minidrone", "Piloting", "FlatTrim")
        self.drone_connection.send_noparam_command_packet_ack(command_tuple)


class Mambo(Minidrone):

    def disconnect(self):
        """
        Disconnect the BLE connection.  Always call this at the end of your programs to
        cleanly disconnect.

        :return: void
        """
        self.drone_connection.disconnect()
        if self.groundcam is not None:
            self.groundcam._close()


    def fire_gun(self):
        """
        Fire the gun (assumes it is attached) - note not supposed under wifi since the camera takes the place of the gun

        :return: True if the command was sent and False otherwise (can include errors or asking to do this using wifi)
        """

        # not supposed under wifi since the camera takes the place of the gun
        if (self.use_wifi):
            return False

        # print "firing gun"
        (command_tuple, enum_tuple) = self.command_parser.get_command_tuple_with_enum("minidrone", "UsbAccessory", "GunControl", "FIRE")
        # print command_tuple
        # print enum_tuple

        return self.drone_connection.send_enum_command_packet_ack(command_tuple, enum_tuple, self.sensors.gun_id)

class Swing(Minidrone):

    def disconnect(self):
        """
        Disconnect the BLE connection.  Always call this at the end of your programs to
        cleanly disconnect.

        :return: void
        """
        self.drone_connection.disconnect()


    def set_flying_mode(self, mode):
        """
        Set drone flying mode

        :param state:
        :return:
        """
        if (mode not in ('quadricopter', 'plane_forward', 'plane_backward')):
            print("Error: %s is not a valid value. The value must be: quadricopter, plane_forward, plane_backward" % mode)
            print("Ignoring command and returning")
            return

        self.set_plane_gear_box(self.sensors.plane_gear_box)

        (command_tuple, enum_tuple) = self.command_parser.get_command_tuple_with_enum("minidrone", "Piloting", "FlyingMode", mode)
        self.drone_connection.send_enum_command_packet_ack(command_tuple, enum_tuple)


    def set_plane_gear_box(self, state):
        """
        Set plane gear box

        :param state:
        :return:
        """
        if (state not in ('gear_1', 'gear_2', 'gear_3')):
            print("Error: %s is not a valid value. The value must be: gear_1, gear_2, gear_3" % state)
            print("Ignoring command and returning")
            return

        (command_tuple, enum_tuple) = self.command_parser.get_command_tuple_with_enum("minidrone", "Piloting", "PlaneGearBox", state)
        self.drone_connection.send_enum_command_packet_ack(command_tuple, enum_tuple)
