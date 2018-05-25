"""
Bebop class holds all of the methods needed to pilot the drone from python and to ask for sensor
data back from the drone

Author: Amy McGovern, dramymcgovern@gmail.com
"""
import time
from pyparrot.networking.wifiConnection import WifiConnection
from pyparrot.utils.colorPrint import color_print
from pyparrot.commandsandsensors.DroneCommandParser import DroneCommandParser
from pyparrot.commandsandsensors import DroneSensorParser

class BebopSensors:
    def __init__(self):
        self.sensors_dict = dict()
        self.RelativeMoveEnded = False
        self.CameraMoveEnded_tilt = False
        self.CameraMoveEnded_pan = False
        self.flying_state = "unknown"

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

        if (sensor_name == "PilotingEvent_moveByEnd"):
            self.RelativeMoveEnded = True

        if (sensor_name == "OrientationV2_tilt"):
            self.CameraMoveEnded_tilt = True

        if (sensor_name == "OrientationV2_pan"):
            self.CameraMoveEnded_pan = True

    def __str__(self):
        str = "Bebop sensors: %s" % self.sensors_dict
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
        #print("data type is %d buffer id is %d sequence number is %d " % (data_type, buffer_id, sequence_number))
        sensor_list = self.sensor_parser.extract_sensor_values(raw_data)
        if (sensor_list is not None):
            for sensor in sensor_list:
                (sensor_name, sensor_value, sensor_enum, header_tuple) = sensor
                if (sensor_name is not None):
                    self.sensors.update(sensor_name, sensor_value, sensor_enum)
                    #print(self.sensors)
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


    def takeoff(self):
        """
        Sends the takeoff command to the mambo.  Gets the codes for it from the xml files.  Ensures the
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

        print("roll is %d pitch is %d yaw is %d vertical is %d" % (my_roll, my_pitch, my_yaw, my_vertical))
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
        command_tuple = self.command_parser.get_command_tuple("ardrone3", "Camera", "OrientationV2")

        self.drone_connection.send_param_command_packet(command_tuple, param_tuple=[tilt_degrees, pan_degrees],
                                                        param_type_tuple=['float', 'float'], ack=False)

    def pan_tilt_camera_velocity(self, tilt_velocity, pan_velocity, duration=0):
        """
        Send the command to tilt the camera by the specified number of degrees per second in pan/tilt.
        This function has two modes.  First, if duration is 0, the initial velocity is sent and
        then the function returns (meaning the camera will keep moving).  If it is greater than 0,
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
