"""
Bebop class holds all of the methods needed to pilot the drone from python and to ask for sensor
data back from the drone

Author: Amy McGovern, dramymcgovern@gmail.com
"""
import time
from pyparrot.networking.wifiConnection import WifiConnection
from pyparrot.utils.colorPrint import color_print
from pyparrot.commandsandsensors.DroneCommandParser import DroneCommandParser
from pyparrot.commandsandsensors.DroneSensorParser import DroneSensorParser
from datetime import datetime

class BebopSensors:
    def __init__(self):
        self.sensors_dict = dict()
        self.RelativeMoveEnded = False
        self.CameraMoveEnded_tilt = False
        self.CameraMoveEnded_pan = False
        self.flying_state = "unknown"
        self.flat_trim_changed = False
        self.max_altitude_changed = False
        self.max_distance_changed = False
        self.no_fly_over_max_distance = False
        self.max_tilt_changed = False
        self.max_pitch_roll_rotation_speed_changed = False
        self.max_vertical_speed_changed = False
        self.max_rotation_speed = False
        self.hull_protection_changed = False
        self.outdoor_mode_changed = False
        self.picture_format_changed = False
        self.auto_white_balance_changed = False
        self.exposition_changed = False
        self.saturation_changed = False
        self.timelapse_changed = False
        self.video_stabilization_changed = False
        self.video_recording_changed = False
        self.video_framerate_changed = False
        self.video_resolutions_changed = False

        # default to full battery
        self.battery = 100

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

    def update(self, sensor_name, sensor_value, sensor_enum):
        if (sensor_name is None):
            print("Error empty sensor")
            return


        if (sensor_name, "enum") in sensor_enum:
            # grab the string value
            if (sensor_value is None or sensor_value > len(sensor_enum[(sensor_name, "enum")])):
                value = "UNKNOWN_ENUM_VALUE"
            else:
                enum_value = sensor_enum[(sensor_name, "enum")][sensor_value]
                value = enum_value

            self.sensors_dict[sensor_name] = value

        else:
            # regular sensor
            self.sensors_dict[sensor_name] = sensor_value

        # some sensors are saved outside the dictionary for internal use (they are also in the dictionary)
        if (sensor_name == "FlyingStateChanged_state"):
            self.flying_state = self.sensors_dict["FlyingStateChanged_state"]

        if (sensor_name == "PilotingState_FlatTrimChanged"):
            self.flat_trim_changed = True

        if (sensor_name == "moveByEnd_dX"):
            self.RelativeMoveEnded = True

        if (sensor_name == "OrientationV2_tilt"):
            self.CameraMoveEnded_tilt = True

        if (sensor_name == "OrientationV2_pan"):
            self.CameraMoveEnded_pan = True

        if (sensor_name == "MaxAltitudeChanged_current"):
            self.max_altitude_changed = True

        if (sensor_name == "MaxDistanceChanged_current"):
            self.max_distance_changed = True

        if (sensor_name == "NoFlyOverMaxDistanceChanged_shouldNotFlyOver"):
            self.no_fly_over_max_distance_changed = True

        if (sensor_name == "MaxTiltChanged_current"):
            self.max_tilt_changed = True

        if (sensor_name == "MaxPitchRollRotationSpeedChanged_current"):
            self.max_pitch_roll_rotation_speed_changed = True

        if (sensor_name == "MaxVerticalSpeedChanged_current"):
            self.max_vertical_speed_changed = True

        if (sensor_name == "MaxRotationSpeedChanged_current"):
            self.max_rotation_speed_changed = True

        if (sensor_name == "HullProtectionChanged_present"):
            self.hull_protection_changed = True

        if (sensor_name == "OutdoorChanged_present"):
            self.outdoor_mode_changed = True

        if (sensor_name == "BatteryStateChanged_battery_percent"):
            self.battery = sensor_value

        if (sensor_name == "PictureFormatChanged_type"):
            self.picture_format_changed = True

        if (sensor_name == "AutoWhiteBalanceChanged_type"):
            self.auto_white_balance_changed = True

        if (sensor_name == "ExpositionChanged_value"):
            self.exposition_changed = True

        if (sensor_name == "SaturationChanged_value"):
            self.saturation_changed = True

        if (sensor_name == "TimelapseChanged_enabled"):
            self.timelapse_changed = True

        if (sensor_name == "VideoStabilizationModeChanged_mode"):
            self.video_stabilization_changed = True

        if (sensor_name == "VideoRecordingModeChanged_mode"):
            self.video_recording_changed = True

        if (sensor_name == "VideoFramerateChanged_framerate"):
            self.video_framerate_changed = True

        if (sensor_name == "VideoResolutionsChanged_type"):
            self.video_resolutions_changed = True

        # call the user callback if it isn't None
        if (self.user_callback_function is not None):
            self.user_callback_function(self.user_callback_function_args)


    def __str__(self):
        str = "Bebop sensors: %s" % self.sensors_dict
        return str

class Bebop():
    def __init__(self, drone_type="Bebop2", ip_address=None):
        """
        Create a new Bebop object.  Assumes you have connected to the Bebop's wifi

        """
        self.drone_type = drone_type

        self.drone_connection = WifiConnection(self, drone_type=drone_type, ip_address=ip_address)

        # intialize the command parser
        self.command_parser = DroneCommandParser()

        # initialize the sensors and the parser
        self.sensors = BebopSensors()
        self.sensor_parser = DroneSensorParser(drone_type=drone_type)

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
        #print("data type is %d buffer id is %d sequence number is %d " % (data_type, buffer_id, sequence_number))
        sensor_list = self.sensor_parser.extract_sensor_values(raw_data)
        #print(sensor_list)
        if (sensor_list is not None):
            for sensor in sensor_list:
                (sensor_name, sensor_value, sensor_enum, header_tuple) = sensor
                if (sensor_name is not None):
                    self.sensors.update(sensor_name, sensor_value, sensor_enum)
                else:
                    color_print("data type %d buffer id %d sequence number %d" % (data_type, buffer_id, sequence_number), "WARN")
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

    def flat_trim(self, duration=0):
        """
        Sends the flat_trim command to the bebop. Gets the codes for it from the xml files.
        :param duration: if duration is greater than 0, waits for the trim command to be finished or duration to be reached
        """
        command_tuple = self.command_parser.get_command_tuple("ardrone3", "Piloting", "FlatTrim")
        self.drone_connection.send_noparam_command_packet_ack(command_tuple)

        if (duration > 0):
            # wait for the specified duration
            start_time = datetime.now()
            new_time = datetime.now()
            diff = (new_time - start_time).seconds + ((new_time - start_time).microseconds / 1000000.0)

            while (not self.sensors.flat_trim_changed and diff < duration):
                self.smart_sleep(0.1)

                new_time = datetime.now()
                diff = (new_time - start_time).seconds + ((new_time - start_time).microseconds / 1000000.0)




    def takeoff(self):
        """
        Sends the takeoff command to the bebop.  Gets the codes for it from the xml files.  Ensures the
        packet was received or sends it again up to a maximum number of times.

        :return: True if the command was sent and False otherwise
        """
        command_tuple = self.command_parser.get_command_tuple("ardrone3", "Piloting", "TakeOff")
        self.drone_connection.send_noparam_command_packet_ack(command_tuple)

    def safe_takeoff(self, timeout):
        """
        Sends commands to takeoff until the Bebop reports it is taking off

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
        Sends the land command to the bebop.  Gets the codes for it from the xml files.  Ensures the
        packet was received or sends it again up to a maximum number of times.

        :return: True if the command was sent and False otherwise
        """
        command_tuple = self.command_parser.get_command_tuple("ardrone3", "Piloting", "Landing")
        return self.drone_connection.send_noparam_command_packet_ack(command_tuple)

    def emergency_land(self):
        """
        Sends the land command to the bebop on the high priority/emergency channel.
        Gets the codes for it from the xml files.  Ensures the
        packet was received or sends it again up to a maximum number of times.

        :return: True if the command was sent and False otherwise
        """
        command_tuple = self.command_parser.get_command_tuple("ardrone3", "Piloting", "Landing")
        return self.drone_connection.send_noparam_high_priority_command_packet(command_tuple)

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
        Ensure the Bebop lands by sending the command until it shows landed on sensors
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

        # print("roll is %d pitch is %d yaw is %d vertical is %d" % (my_roll, my_pitch, my_yaw, my_vertical))
        command_tuple = self.command_parser.get_command_tuple("ardrone3", "Piloting", "PCMD")

        self.drone_connection.send_pcmd_command(command_tuple, my_roll, my_pitch, my_yaw, my_vertical, duration)


    def flip(self, direction):
        """
        Sends the flip command to the bebop.  Gets the codes for it from the xml files. Ensures the
        packet was received or sends it again up to a maximum number of times.
        Valid directions to flip are: front, back, right, left

        :return: True if the command was sent and False otherwise
        """
        fixed_direction = direction.lower()
        if (fixed_direction not in ("front", "back", "right", "left")):
            print("Error: %s is not a valid direction.  Must be one of %s" % direction, "front, back, right, or left")
            print("Ignoring command and returning")
            return

        (command_tuple, enum_tuple) = self.command_parser.get_command_tuple_with_enum("ardrone3",
                                                                                      "Animations", "Flip", fixed_direction)
        # print command_tuple
        # print enum_tuple

        return self.drone_connection.send_enum_command_packet_ack(command_tuple, enum_tuple)

    def move_relative(self, dx, dy, dz, dradians):
        """
        Move relative to our current position and pause until the command is done.  Note that
        EVERY time we tested flying relative up (e.g. negative z) it did additional lateral moves
        that were unnecessary.  I'll be posting this to the development board but, until then,
        I recommend only using dx, dy, and dradians which all seem to work well.

        :param dx: change in front axis (meters)
        :param dy: change in right/left (positive is right) (meters)
        :param dz: change in height (positive is DOWN) (meters)
        :param dradians: change in heading in radians

        :return: nothing
        """

        command_tuple = self.command_parser.get_command_tuple("ardrone3", "Piloting", "moveBy")
        param_tuple = [dx, dy, dz, dradians]  # Enable
        param_type_tuple = ['float', 'float', 'float', 'float']
        #reset the bit that tells when the move ends
        self.sensors.RelativeMoveEnded = False

        # send the command
        self.drone_connection.send_param_command_packet(command_tuple, param_tuple, param_type_tuple)

        # sleep until it ends
        while (not self.sensors.RelativeMoveEnded):
            self.smart_sleep(0.01)


    def start_video_stream(self):
        """
        Sends the start stream command to the bebop. The bebop will start streaming
        RTP packets on the port defined in wifiConnection.py (55004 by default).
        The packets can be picked up by opening an approriate SDP file in a media
        player such as VLC, MPlayer, FFMPEG or OpenCV.

        :return: nothing
        """

        command_tuple = self.command_parser.get_command_tuple("ardrone3", "MediaStreaming", "VideoEnable")
        param_tuple = [1] # Enable
        param_type_tuple = ['u8']
        self.drone_connection.send_param_command_packet(command_tuple,param_tuple,param_type_tuple)


    def stop_video_stream(self):
        """
        Sends the stop stream command to the bebop. The bebop will stop streaming
        RTP packets.

        :return: nothing
        """

        command_tuple = self.command_parser.get_command_tuple("ardrone3", "MediaStreaming", "VideoEnable")
        param_tuple = [0] # Disable
        param_type_tuple = ['u8']
        self.drone_connection.send_param_command_packet(command_tuple,param_tuple,param_type_tuple)


    def set_video_stream_mode(self,mode='low_latency'):
        """
        Set the video mode for the RTP stream.
        :param: mode: one of 'low_latency', 'high_reliability' or 'high_reliability_low_framerate'

        :return: True if the command was sent and False otherwise
        """

        # handle case issues
        fixed_mode = mode.lower()

        if (fixed_mode not in ("low_latency", "high_reliability", "high_reliability_low_framerate")):
            print("Error: %s is not a valid stream mode.  Must be one of %s" % (mode, "low_latency, high_reliability or high_reliability_low_framerate"))
            print("Ignoring command and returning")
            return False


        (command_tuple, enum_tuple) = self.command_parser.get_command_tuple_with_enum("ardrone3",
                                                                                      "MediaStreaming", "VideoStreamMode", mode)

        return self.drone_connection.send_enum_command_packet_ack(command_tuple,enum_tuple)

    def pan_tilt_camera(self, tilt_degrees, pan_degrees):
        """
        Send the command to pan/tilt the camera by the specified number of degrees in pan/tilt

        Note, this only seems to work in small increments.  Use pan_tilt_velocity to get the camera to look
        straight downward

        :param tilt_degrees: tilt degrees
        :param pan_degrees: pan degrees
        :return:
        """
        if(self.drone_type == "Bebop2"):
            command_tuple = self.command_parser.get_command_tuple("ardrone3", "Camera", "OrientationV2")

            self.drone_connection.send_param_command_packet(command_tuple, param_tuple=[tilt_degrees, pan_degrees],
                                                            param_type_tuple=['float', 'float'], ack=False)
        else:
            command_tuple = self.command_parser.get_command_tuple("ardrone3", "Camera", "Orientation")

            self.drone_connection.send_param_command_packet(command_tuple, param_tuple=[tilt_degrees, pan_degrees],
                                                            param_type_tuple=['i8', 'i8'], ack=False)

    def pan_tilt_camera_velocity(self, tilt_velocity, pan_velocity, duration=0):
        """
        Send the command to tilt the camera by the specified number of degrees per second in pan/tilt.
        This function has two modes.  First, if duration is 0, the initial velocity is sent and
        then the function returns (meaning the camera will keep moving).  If duration is greater than 0,
        the command executes for that amount of time and then sends a stop command to the camera
        and then returns.

        :param tilt_degrees: tile change in degrees per second
        :param pan_degrees: pan change in degrees per second
        :param duration: seconds to run the command for
        :return:
        """
        command_tuple = self.command_parser.get_command_tuple("ardrone3", "Camera", "Velocity")

        self.drone_connection.send_param_command_packet(command_tuple, param_tuple=[tilt_velocity, pan_velocity],
                                                        param_type_tuple=['float', 'float'], ack=False)


        if (duration > 0):
            # wait for the specified duration
            start_time = time.time()
            while (time.time() - start_time < duration):
                self.drone_connection.smart_sleep(0.1)

            # send the stop command
            self.drone_connection.send_param_command_packet(command_tuple, param_tuple=[0, 0],
                                                            param_type_tuple=['float', 'float'], ack=False)

    def set_max_altitude(self, altitude):
        """
        Set max altitude in meters.

        :param altitude: altitude in meters
        :return:
        """
        if (altitude < 0.5 or altitude > 150):
            print("Error: %s is not valid altitude. The altitude must be between 0.5 and 150 meters" % altitude)
            print("Ignoring command and returning")
            return

        command_tuple = self.command_parser.get_command_tuple("ardrone3", "PilotingSettings", "MaxAltitude")
        self.drone_connection.send_param_command_packet(command_tuple, param_tuple=[altitude], param_type_tuple=['float'])

        while (not self.sensors.max_altitude_changed):
            self.smart_sleep(0.1)

    def set_max_distance(self, distance):
        """
        Set max distance between the takeoff and the drone in meters.

        :param distance: distance in meters
        :return:
        """
        if (distance < 10 or distance > 2000):
            print("Error: %s is not valid altitude. The distance must be between 10 and 2000 meters" % distance)
            print("Ignoring command and returning")
            return

        command_tuple = self.command_parser.get_command_tuple("ardrone3", "PilotingSettings", "MaxDistance")

        self.sensors.max_distance_changed = False

        self.drone_connection.send_param_command_packet(command_tuple, param_tuple=[distance], param_type_tuple=['float'])

        while (not self.sensors.max_distance_changed):
            self.smart_sleep(0.1)

    def enable_geofence(self, value):
        """
	     If geofence is enabled, the drone won't fly over the given max distance.
         1 if the drone can't fly further than max distance, 0 if no limitation on the drone should be done.

        :param value:
        :return:
        """
        if (value not in (0, 1)):
            print("Error: %s is not valid value. Valid value: 1 to enable geofence/ 0 to disable geofence" % value)
            print("Ignoring command and returning")
            return

        command_tuple = self.command_parser.get_command_tuple("ardrone3", "PilotingSettings", "NoFlyOverMaxDistance")
        self.drone_connection.send_param_command_packet(command_tuple, param_tuple=[value], param_type_tuple=['u8'])

        while (not self.sensors.no_fly_over_max_distance_changed):
            self.smart_sleep(0.1)

    def set_max_tilt(self, tilt):
        """
        Set max pitch/roll in degrees

        :param tilt: max tilt for both pitch and roll in degrees
        :return:
        """
        if (tilt < 5 or tilt > 30):
            print("Error: %s is not valid tilt. The tilt must be between 5 and 30 degrees" % tilt)
            print("Ignoring command and returning")
            return

        command_tuple = self.command_parser.get_command_tuple("ardrone3", "PilotingSettings", "MaxTilt")
        self.drone_connection.send_param_command_packet(command_tuple, param_tuple=[tilt], param_type_tuple=['float'])

        while (not self.sensors.max_tilt_changed):
            self.smart_sleep(0.1)

    def set_max_tilt_rotation_speed(self, speed):
        """
        Set max pitch/roll rotation speed in degree/s

        :param speed: max rotation speed for both pitch and roll in degree/s
        :return:
        """
        if (speed < 80 or speed > 300):
            print("Error: %s is not valid speed. The speed must be between 80 and 300 degree/s" % speed)
            print("Ignoring command and returning")
            return

        command_tuple = self.command_parser.get_command_tuple("ardrone3", "SpeedSettings", "MaxPitchRollRotationSpeed")
        self.drone_connection.send_param_command_packet(command_tuple, param_tuple=[speed], param_type_tuple=['float'])

        while (not self.sensors.max_pitch_roll_rotation_speed_changed):
            self.smart_sleep(0.1)

    def set_max_vertical_speed(self, speed):
        """
        Set max vertical speed in m/s

        :param speed: max vertical speed in m/s
        :return:
        """
        if (speed < 0.5 or speed > 2.5):
            print("Error: %s is not valid speed. The speed must be between 0.5 and 2.5 m/s" % speed)
            print("Ignoring command and returning")
            return

        command_tuple = self.command_parser.get_command_tuple("ardrone3", "SpeedSettings", "MaxVerticalSpeed")
        self.drone_connection.send_param_command_packet(command_tuple, param_tuple=[speed], param_type_tuple=['float'])

        while (not self.sensors.max_vertical_speed_changed):
            self.smart_sleep(0.1)

    def set_max_rotation_speed(self, speed):
        """
        Set max yaw rotation speed in degree/s

        :param speed: max rotation speed for yaw in degree/s
        :return:
        """
        if (speed < 10 or speed > 200):
            print("Error: %s is not valid speed. The speed must be between 10 and 200 degree/s" % speed)
            print("Ignoring command and returning")
            return

        command_tuple = self.command_parser.get_command_tuple("ardrone3", "SpeedSettings", "MaxRotationSpeed")
        self.drone_connection.send_param_command_packet(command_tuple, param_tuple=[speed], param_type_tuple=['float'])

        while (not self.sensors.max_rotation_speed_changed):
            self.smart_sleep(0.1)

    def set_hull_protection(self, present):
        """
        Set the presence of hull protection - this is only needed for bebop 1
       	1 if present, 0 if not present

        :param present:
        :return:
        """
        if (present not in (0, 1)):
            print("Error: %s is not valid value. The value must be 0 or 1" % present)
            print("Ignoring command and returning")
            return

        command_tuple = self.command_parser.get_command_tuple("ardrone3", "SpeedSettings", "HullProtection")
        self.drone_connection.send_param_command_packet(command_tuple, param_tuple=[present], param_type_tuple=['u8'])

        while (not self.sensors.hull_protection_changed):
            self.smart_sleep(0.1)

    def set_indoor(self, is_outdoor):
        """
        Set bebop 1 to indoor mode (not used in bebop 2!!)
       	1 if outdoor, 0 if indoor

        :param present:
        :return:
        """
        if (is_outdoor not in (0, 1)):
            print("Error: %s is not valid value. The value must be 0 or 1" % is_outdoor)
            print("Ignoring command and returning")
            return

        command_tuple = self.command_parser.get_command_tuple("ardrone3", "SpeedSettings", "Outdoor")
        self.drone_connection.send_param_command_packet(command_tuple, param_tuple=[is_outdoor], param_type_tuple=['u8'])

        #while (not self.sensors.outdoor_mode_changed):
        #    self.smart_sleep(0.1)

    def set_picture_format(self, format):
        """
        Set picture format

        :param format:
        :return:
        """
        if (format not in ('raw', 'jpeg', 'snapshot', 'jpeg_fisheye')):
            print("Error: %s is not valid value. The value must be : raw, jpeg, snapshot, jpeg_fisheye" % format)
            print("Ignoring command and returning")
            return

        (command_tuple, enum_tuple) = self.command_parser.get_command_tuple_with_enum("ardrone3", "PictureSettings", "PictureFormatSelection", format)
        self.drone_connection.send_enum_command_packet_ack(command_tuple, enum_tuple)

        while (not self.sensors.picture_format_changed):
            self.smart_sleep(0.1)

    def set_white_balance(self, type):
        """
        Set white balance

        :param type:
        :return:
        """
        if (type not in ('auto', 'tungsten', 'daylight', 'cloudy', 'cool_white')):
            print("Error: %s is not valid value. The value must be : auto, tungsten, daylight, cloudy, cool_white" % type)
            print("Ignoring command and returning")
            return

        (command_tuple, enum_tuple) = self.command_parser.get_command_tuple_with_enum("ardrone3", "PictureSettings", "AutoWhiteBalanceSelection", type)
        self.drone_connection.send_enum_command_packet_ack(command_tuple, enum_tuple)

        while (not self.sensors.auto_white_balance_changed):
            self.smart_sleep(0.1)

    def set_exposition(self, value):
        """
        Set image exposure

        :param value:
        :return:
        """
        if (value < -1.5 or value > 1.5):
            print("Error: %s is not valid image exposure. The value must be between -1.5 and 1.5." % value)
            print("Ignoring command and returning")
            return

        command_tuple = self.command_parser.get_command_tuple("ardrone3", "PictureSettings", "ExpositionSelection")
        self.drone_connection.send_param_command_packet(command_tuple, param_tuple=[value], param_type_tuple=['float'])

        while (not self.sensors.exposition_changed):
            self.smart_sleep(0.1)

    def set_saturation(self, value):
        """
        Set image saturation

        :param value:
        :return:
        """
        if (value < -100 or value > 100):
            print("Error: %s is not valid image saturation. The value must be between -100 and 100." % value)
            print("Ignoring command and returning")
            return

        command_tuple = self.command_parser.get_command_tuple("ardrone3", "PictureSettings", "SaturationSelection")
        self.drone_connection.send_param_command_packet(command_tuple, param_tuple=[value], param_type_tuple=['float'])

        while (not self.sensors.saturation_changed):
            self.smart_sleep(0.1)

    def set_timelapse(self, enable, interval=8):
        """
        Set timelapse mode

        :param enable:
        :param interval:
        :return:
        """
        if (enable not in (0, 1) or interval < 8 or interval > 300):
            print("Error: %s or %s is not valid value." % (enable, interval))
            print("Ignoring command and returning")
            return

        command_tuple = self.command_parser.get_command_tuple("ardrone3", "PictureSettings", "TimelapseSelection")
        self.drone_connection.send_param_command_packet(command_tuple, param_tuple=[enable, interval], param_type_tuple=['u8', 'float'])

        while (not self.sensors.timelapse_changed):
            self.smart_sleep(0.1)

    def set_video_stabilization(self, mode):
        """
        Set video stabilization mode

        :param mode:
        :return:
        """
        if (mode not in ('roll_pitch', 'pitch', 'roll', 'none')):
            print("Error: %s is not valid value. The value must be : roll_pitch, pitch, roll, none" % mode)
            print("Ignoring command and returning")
            return

        (command_tuple, enum_tuple) = self.command_parser.get_command_tuple_with_enum("ardrone3", "PictureSettings", "VideoStabilizationMode", mode)
        self.drone_connection.send_enum_command_packet_ack(command_tuple, enum_tuple)

        while (not self.sensors.video_stabilization_changed):
            self.smart_sleep(0.1)

    def set_video_recording(self, mode):
        """
        Set video recording mode

        :param mode:
        :return:
        """
        if (mode not in ('quality', 'time')):
            print("Error: %s is not valid value. The value must be : quality, time" % mode)
            print("Ignoring command and returning")
            return

        (command_tuple, enum_tuple) = self.command_parser.get_command_tuple_with_enum("ardrone3", "PictureSettings", "VideoRecordingMode", mode)
        self.drone_connection.send_enum_command_packet_ack(command_tuple, enum_tuple)

        while (not self.sensors.video_recording_changed):
            self.smart_sleep(0.1)

    def set_video_framerate(self, framerate):
        """
        Set video framerate

        :param framerate:
        :return:
        """
        if (framerate not in ('24_FPS', '25_FPS', '30_FPS')):
            print("Error: %s is not valid value. The value must be : 24_FPS, 25_FPS, 30_FPS" % framerate)
            print("Ignoring command and returning")
            return

        (command_tuple, enum_tuple) = self.command_parser.get_command_tuple_with_enum("ardrone3", "PictureSettings", "VideoFramerate", framerate)
        self.drone_connection.send_enum_command_packet_ack(command_tuple, enum_tuple)

        while (not self.sensors.video_framerate_changed):
            self.smart_sleep(0.1)

    def set_video_resolutions(self, type):
        """
        Set video resolutions

        :param type:
        :return:
        """
        if (type not in ('rec1080_stream480', 'rec720_stream720')):
            print("Error: %s is not valid value. The value must be : rec1080_stream480, rec720_stream720" % type)
            print("Ignoring command and returning")
            return

        (command_tuple, enum_tuple) = self.command_parser.get_command_tuple_with_enum("ardrone3", "PictureSettings", "VideoResolutions", type)
        self.drone_connection.send_enum_command_packet_ack(command_tuple, enum_tuple)

        while (not self.sensors.video_resolutions_changed):
            self.smart_sleep(0.1)
