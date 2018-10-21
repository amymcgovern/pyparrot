"""
Holds all the data and commands needed to fly a Bebop drone.

Author: Amy McGovern, dramymcgovern@gmail.com
"""

from zeroconf import ServiceBrowser, Zeroconf
from datetime import datetime
import time
import socket
import ipaddress
import json
from pyparrot.utils.colorPrint import color_print
import struct
import threading
from pyparrot.commandsandsensors.DroneSensorParser import get_data_format_and_size

class mDNSListener(object):
    """
    This is adapted from the listener code at

    https://pypi.python.org/pypi/zeroconf
    """
    def __init__(self, wifi_connection):
        self.wifi_connection = wifi_connection

    def remove_service(self, zeroconf, type, name):
        #print("Service %s removed" % (name,))
        pass

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        print("Service %s added, service info: %s" % (name, info))
        self.wifi_connection._connect_listener_called(info)



class WifiConnection:

    def __init__(self, drone, drone_type="Bebop2"):
        """
        Can be a connection to a Bebop, Bebop2 or a Mambo right now

        :param type: type of drone to connect to
        """
        self.is_connected = False
        if (drone_type not in ("Bebop", "Bebop2", "Mambo")):
            color_print("Error: only type Bebop and Mambo are currently supported", "ERROR")
            return

        self.drone = drone

        self.drone_type = drone_type
        self.udp_send_port = 44444 # defined during the handshake except not on Mambo after 3.0.26 firmware
        self.udp_receive_port = 43210
        self.is_listening = True  # for the UDP listener

        if (drone_type is "Bebop"):
            self.mdns_address = "_arsdk-0901._udp.local."
            #Bebop video streaming
            self.stream_port = 55004
            self.stream_control_port = 55005
        elif (drone_type is "Bebop2"):
            self.mdns_address = "_arsdk-090c._udp.local."
            #Bebop video streaming
            self.stream_port = 55004
            self.stream_control_port = 55005
        elif (drone_type is "Mambo"):
            self.mdns_address = "_arsdk-090b._udp.local."

        # map of the data types by name (for outgoing packets)
        self.data_types_by_name = {
            'ACK' : 1,
            'DATA_NO_ACK': 2,
            'LOW_LATENCY_DATA': 3,
            'DATA_WITH_ACK' : 4
        }

        # map of the incoming data types by number (to figure out if we need to ack etc)
        self.data_types_by_number = {
            1 : 'ACK',
            2 : 'DATA_NO_ACK',
            3 : 'LOW_LATENCY_DATA',
            4 : 'DATA_WITH_ACK'
        }

        self.sequence_counter = {
            'PONG': 0,
            'SEND_NO_ACK': 0,
            'SEND_WITH_ACK': 0,
            'SEND_HIGH_PRIORITY': 0,
            'VIDEO_ACK': 0,
            'ACK_DRONE_DATA': 0,
            'NO_ACK_DRONE_DATA': 0,
            'VIDEO_DATA': 0,
        }

        self.buffer_ids = {
            'PING': 0,                  # pings from device
            'PONG': 1,                  # respond to pings
            'SEND_NO_ACK': 10,           # not-ack commandsandsensors (piloting and camera rotations)
            'SEND_WITH_ACK': 11,         # ack commandsandsensors (all piloting commandsandsensors)
            'SEND_HIGH_PRIORITY': 12,    # emergency commandsandsensors
            'VIDEO_ACK': 13,               # ack for video
            'ACK_DRONE_DATA' : 127,        # drone data that needs an ack
            'NO_ACK_DRONE_DATA' : 126,     # data from drone (including battery and others), no ack
            'VIDEO_DATA' : 125,            # video data
            'ACK_FROM_SEND_WITH_ACK': 139  # 128 + buffer id for 'SEND_WITH_ACK' is 139
            }

        self.data_buffers = (self.buffer_ids['ACK_DRONE_DATA'], self.buffer_ids['NO_ACK_DRONE_DATA'])

        # store whether a command was acked
        self.command_received = {
            'SEND_WITH_ACK': False,
            'SEND_HIGH_PRIORITY': False,
            'ACK_COMMAND': False
        }

        # maximum number of times to try a packet before assuming it failed
        self.max_packet_retries = 1

        # threading lock for waiting
        self._lock = threading.Lock()


    def connect(self, num_retries):
        """
        Connects to the drone

        :param num_retries: maximum number of retries

        :return: True if the connection succeeded and False otherwise
        """

        if ("Mambo" not in self.drone_type):
            print("Setting up mDNS listener since this is not a Mambo")
            #parrot's latest mambo firmware (3.0.26 broke all of the mDNS services so this is (temporarily) commented
            #out but it is backwards compatible and will work with the hard-coded addresses for now.
            zeroconf = Zeroconf()
            listener = mDNSListener(self)

            print("Making a browser for %s" % self.mdns_address)

            browser = ServiceBrowser(zeroconf, self.mdns_address , listener)

            # basically have to sleep until the info comes through on the listener
            num_tries = 0
            while (num_tries < num_retries and not self.is_connected):
                time.sleep(1)
                num_tries += 1

            # if we didn't hear the listener, return False
            if (not self.is_connected):
                color_print("connection failed: did you remember to connect your machine to the Drone's wifi network?", "ERROR")
                return False
            else:
                browser.cancel()

        # perform the handshake and get the UDP info
        handshake = self._handshake(num_retries)
        if (handshake):
            self._create_udp_connection()
            self.listener_thread = threading.Thread(target=self._listen_socket)
            self.listener_thread.start()

            color_print("Success in setting up the wifi network to the drone!", "SUCCESS")
            return True
        else:
            color_print("Error: TCP handshake failed.", "ERROR")
            return False

    def _listen_socket(self):
        """
        Listens to the socket and sleeps in between receives.
        Runs forever (until disconnect is called)
        """

        print("starting listening at ")
        data = None

        while (self.is_listening):
            try:
                (data, address) = self.udp_receive_sock.recvfrom(66000)

            except socket.timeout:
                print("timeout - trying again")

            except:
                pass

            self.handle_data(data)

        color_print("disconnecting", "INFO")
        self.disconnect()

    def handle_data(self, data):
        """
        Handles the data as it comes in

        :param data: raw data packet
        :return:
        """
        # got the idea to of how to handle this data nicely (handling the perhaps extra data in the packets)
        # and unpacking the critical info first (id, size etc) from
        # https://github.com/N-Bz/bybop/blob/8d4c569c8e66bd1f0fdd768851409ca4b86c4ecd/src/Bybop_NetworkAL.py

        my_data = data

        while (my_data):
            #print("inside loop to handle data ")
            (data_type, buffer_id, packet_seq_id, packet_size) = struct.unpack('<BBBI', my_data[0:7])
            recv_data = my_data[7:packet_size]

            #print("\tgot a data type of of %d " % data_type)
            #print("\tgot a buffer id of of %d " % buffer_id)
            #print("\tgot a packet seq id of of %d " % packet_seq_id)
            #print("\tsize is %d" % packet_size)
            self.handle_frame(data_type, buffer_id, packet_seq_id, recv_data)

            # loop in case there is more data
            my_data = my_data[packet_size:]
            #print("assigned more data")
        #print("ended loop handling data")

    def handle_frame(self, packet_type, buffer_id, packet_seq_id, recv_data):
        if (buffer_id == self.buffer_ids['PING']):
            #color_print("this is a ping!  need to pong", "INFO")
            self._send_pong(recv_data)

        if (self.data_types_by_number[packet_type] == 'ACK'):
            #print("setting command received to true")
            ack_seq = int(struct.unpack("<B", recv_data)[0])
            self._set_command_received('SEND_WITH_ACK', True, ack_seq)
            self.ack_packet(buffer_id, ack_seq)
        elif (self.data_types_by_number[packet_type] == 'DATA_NO_ACK'):
            #print("DATA NO ACK")
            if (buffer_id in self.data_buffers):
                self.drone.update_sensors(packet_type, buffer_id, packet_seq_id, recv_data, ack=False)
        elif (self.data_types_by_number[packet_type] == 'LOW_LATENCY_DATA'):
            print("Need to handle Low latency data")
        elif (self.data_types_by_number[packet_type] == 'DATA_WITH_ACK'):
            #print("DATA WITH ACK")
            if (buffer_id in self.data_buffers):
                self.drone.update_sensors(packet_type, buffer_id, packet_seq_id, recv_data, ack=True)
        else:
            color_print("HELP ME", "ERROR")
            print("got a different type of data - help")

    def _send_pong(self, data):
        """
        Send a PONG back to a PING

        :param data: data that needs to be PONG/ACK'd
        :return: nothing
        """

        size = len(data)

        self.sequence_counter['PONG'] = (self.sequence_counter['PONG'] + 1) % 256

        packet = struct.pack("<BBBI", self.data_types_by_name['DATA_NO_ACK'], self.buffer_ids['PONG'],
                             self.sequence_counter['PONG'], size + 7)
        packet += data
        self.safe_send(packet)



    def _set_command_received(self, channel, val, seq_id):
        """
        Set the command received on the specified channel to the specified value (used for acks)

        :param channel: channel
        :param val: True or False
        :return:
        """
        self.command_received[(channel, seq_id)] = val

    def _is_command_received(self, channel, seq_id):
        """
        Is the command received?

        :param channel: channel it was sent on
        :param seq_id: sequence id of the command
        :return:
        """
        return self.command_received[(channel, seq_id)]

    def _handshake(self, num_retries):
        """
        Performs the handshake over TCP to get all the connection info

        :return: True if it worked and False otherwise
        """

        # create the TCP socket for the handshake
        tcp_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        #print (self.connection_info.address, self.connection_info.port)
        #print(ipaddress.IPv4Address(self.connection_info.address))

        # connect
        # handle the broken mambo firmware by hard-coding the port and IP address
        if ("Mambo" in self.drone_type):
            self.drone_ip = "192.168.99.3"
            tcp_sock.connect(("192.168.99.3", 44444))
        else:
            self.drone_ip = ipaddress.IPv4Address(self.connection_info.address).exploded
            tcp_sock.connect((self.drone_ip, self.connection_info.port))

        # send the handshake information
        if(self.drone_type in ("Bebop", "Bebop2")):
            # For Bebop add video stream ports to the json request
            json_string = json.dumps({"d2c_port":self.udp_receive_port,
                                      "controller_type":"computer",
                                      "controller_name":"pyparrot",
                                      "arstream2_client_stream_port":self.stream_port,
                                      "arstream2_client_control_port":self.stream_control_port})
        else:
            json_string = json.dumps({"d2c_port":self.udp_receive_port,
                                      "controller_type":"computer",
                                      "controller_name":"pyparrot"})
            
        json_obj = json.loads(json_string)
        print(json_string)
        try:
            # python 3
            tcp_sock.send(bytes(json_string, 'utf-8'))
        except:
            # python 2
            tcp_sock.send(json_string)


        # wait for the response
        finished = False
        num_try = 0
        while (not finished and num_try < num_retries):
            data = tcp_sock.recv(4096).decode('utf-8')
            if (len(data) > 0):
                my_data = data[0:-1]
                self.udp_data = json.loads(str(my_data))

                # if the drone refuses the connection, return false
                if (self.udp_data['status'] != 0):
                    return False

                print(self.udp_data)
                self.udp_send_port = self.udp_data['c2d_port']
                print("c2d_port is %d" % self.udp_send_port)
                finished = True
            else:
                num_try += 1

        # cleanup
        tcp_sock.close()

        return finished


    def _create_udp_connection(self):
        """
        Create the UDP connection
        """
        self.udp_send_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        #self.udp_send_sock.connect((self.drone_ip, self.udp_send_port))

        self.udp_receive_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        # don't use the connect, use bind instead
        # learned from bybop code
        # https://github.com/N-Bz/bybop/blob/8d4c569c8e66bd1f0fdd768851409ca4b86c4ecd/src/Bybop_NetworkAL.py
        #self.udp_receive_sock.connect((self.drone_ip, self.udp_receive_port))
        self.udp_receive_sock.settimeout(5.0)
        self.udp_receive_sock.bind(('0.0.0.0', int(self.udp_receive_port)))


    def _connect_listener_called(self, connection_info):
        """
        Save the connection info and set the connected to be true.  This si called within the listener
        for the connection.

        :param connection_info:
        :return:
        """
        self.connection_info = connection_info
        self.is_connected = True

    def disconnect(self):
        """
        Disconnect cleanly from the sockets
        """
        self.is_listening = False

        # Sleep for a moment to allow all socket activity to cease before closing
        # This helps to avoids a Winsock error regarding a operations on a closed socket
        self.smart_sleep(0.5)

        # then put the close in a try/except to catch any further winsock errors
        # the errors seem to be mostly occurring on windows for some reason
        try:
            self.udp_receive_sock.close()
            self.udp_send_sock.close()
        except:
            pass

    def safe_send(self, packet):

        packet_sent = False
        #print "inside safe send"

        try_num = 0

        while (not packet_sent and try_num < self.max_packet_retries):
            try:
                self.udp_send_sock.sendto(packet, (self.drone_ip, self.udp_send_port))
                packet_sent = True
            except:
                #print "resetting connection"
                self.udp_send_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
                #self.udp_send_sock.connect((self.drone_ip, self.udp_send_port))
                try_num += 1


    def send_command_packet_ack(self, packet, seq_id):
        """
        Sends the actual packet on the ack channel.  Internal function only.

        :param packet: packet constructed according to the command rules (variable size, constructed elsewhere)
        :return: True if the command was sent and False otherwise
        """
        try_num = 0
        self._set_command_received('SEND_WITH_ACK', False, seq_id)
        while (try_num < self.max_packet_retries and not self._is_command_received('SEND_WITH_ACK', seq_id)):
            color_print("sending packet on try %d", try_num)
            self.safe_send(packet)
            try_num += 1
            self.smart_sleep(0.5)

        return self._is_command_received('SEND_WITH_ACK', seq_id)

    def send_command_packet_noack(self, packet):
        """
        Sends the actual packet on the No-ack channel.  Internal function only.

        :param packet: packet constructed according to the command rules (variable size, constructed elsewhere)
        :return: True if the command was sent and False otherwise
        """
        try_num = 0
        color_print("sending packet on try %d", try_num)
        self.safe_send(packet)

    def send_noparam_high_priority_command_packet(self, command_tuple):
        """
        Send a no parameter command packet on the high priority channel
        :param command_tuple:
        :return:
        """
        self.sequence_counter['SEND_HIGH_PRIORITY'] = (self.sequence_counter['SEND_HIGH_PRIORITY'] + 1) % 256

        packet = struct.pack("<BBBIBBH", self.data_types_by_name['LOW_LATENCY_DATA'],
                             self.buffer_ids['SEND_HIGH_PRIORITY'],
                             self.sequence_counter['SEND_HIGH_PRIORITY'], 11,
                             command_tuple[0], command_tuple[1], command_tuple[2])

        self.safe_send(packet)


    def send_noparam_command_packet_ack(self, command_tuple):
        """
        Send a no parameter command packet on the ack channel
        :param command_tuple:
        :return:
        """
        self.sequence_counter['SEND_WITH_ACK'] = (self.sequence_counter['SEND_WITH_ACK'] + 1) % 256

        packet = struct.pack("<BBBIBBH", self.data_types_by_name['DATA_WITH_ACK'],
                             self.buffer_ids['SEND_WITH_ACK'],
                             self.sequence_counter['SEND_WITH_ACK'], 11,
                             command_tuple[0], command_tuple[1], command_tuple[2])

        return self.send_command_packet_ack(packet, self.sequence_counter['SEND_WITH_ACK'])

    def send_param_command_packet(self, command_tuple, param_tuple=None, param_type_tuple=0,ack=True):
        """
        Send a command packet with parameters. Ack channel is optional for future flexibility,
        but currently commands are always send over the Ack channel so it defaults to True.

        Contributed by awm102 on github

        :param: command_tuple: the command tuple derived from command_parser.get_command_tuple()
        :param: param_tuple (optional): the parameter values to be sent (can be found in the XML files)
        :param: param_size_tuple (optional): a tuple of strings representing the data type of the parameters
        e.g. u8, float etc. (can be found in the XML files)
        :param: ack (optional): allows ack to be turned off if required
        :return:
        """
# TODO: This function could potentially be extended to encompass send_noparam_command_packet_ack
# and send_enum_command_packet_ack if desired for more modular code.
# TODO: The function could be improved by looking up the parameter data types in the xml files
# in the same way the send_enum_command_packet_ack does. 

        # Create lists to store the number of bytes and pack chars needed for parameters
        # Default them to zero so that if no params are provided the packet size is correct 
        param_size_list = [0] * len(param_tuple)
        pack_char_list = [0] * len(param_tuple)
        
        if param_tuple is not None:
            # Fetch the parameter sizes. By looping over the param_tuple we only get the data
            # for requested parameters so a mismatch in params and types does not matter
            for i,param in enumerate(param_tuple):
                pack_char_list[i], param_size_list[i] = get_data_format_and_size(param, param_type_tuple[i])
            
        if ack:
            ack_string = 'SEND_WITH_ACK'
            data_ack_string = 'DATA_WITH_ACK'
        else:
            ack_string = 'SEND_NO_ACK'
            data_ack_string = 'DATA_NO_ACK'

        # Construct the base packet
        self.sequence_counter[ack_string] = (self.sequence_counter[ack_string] + 1) % 256

        # Calculate packet size:
        # base packet <BBBIBBH is 11 bytes, param_size_list can be added up
        packet_size = 11 + sum(param_size_list)
        
        packet = struct.pack("<BBBIBBH", self.data_types_by_name[data_ack_string],
                             self.buffer_ids[ack_string],
                             self.sequence_counter[ack_string], packet_size,
                             command_tuple[0], command_tuple[1], command_tuple[2])

        if param_tuple is not None:
            # Add in the parameter values based on their sizes
            for i,param in enumerate(param_tuple):
                packet += struct.pack(pack_char_list[i],param)

        if ack:
            return self.send_command_packet_ack(packet, self.sequence_counter['SEND_WITH_ACK'])
        else:
            return self.send_command_packet_noack(packet)


    def send_single_pcmd_command(self, command_tuple, roll, pitch, yaw, vertical_movement):
        """
        Send a single PCMD command with the specified roll, pitch, and yaw.  Note
        this will not make that command run forever.  Instead it sends ONCE.  This can be used
        in a loop (in your agent) that makes more smooth control than using the duration option.

        :param command_tuple: command tuple per the parser
        :param roll:
        :param pitch:
        :param yaw:
        :param vertical_movement:
        """
        self.sequence_counter['SEND_NO_ACK'] = (self.sequence_counter['SEND_NO_ACK'] + 1) % 256
        packet = struct.pack("<BBBIBBHBbbbbI",
                             self.data_types_by_name['DATA_NO_ACK'],
                             self.buffer_ids['SEND_NO_ACK'],
                             self.sequence_counter['SEND_NO_ACK'],
                             20,
                             command_tuple[0], command_tuple[1], command_tuple[2],
                             1, roll, pitch, yaw, vertical_movement, 0)

        self.safe_send(packet)

    def send_pcmd_command(self, command_tuple, roll, pitch, yaw, vertical_movement, duration):
        """
        Send the PCMD command with the specified roll, pitch, and yaw

        :param command_tuple: command tuple per the parser
        :param roll:
        :param pitch:
        :param yaw:
        :param vertical_movement:
        :param duration:
        """
        start_time = datetime.now()
        new_time = datetime.now()
        diff = (new_time - start_time).seconds + ((new_time - start_time).microseconds / 1000000.0)

        while (diff < duration):
            self.send_single_pcmd_command(command_tuple, roll, pitch, yaw, vertical_movement)
            self.smart_sleep(0.1)
            new_time = datetime.now()
            diff = (new_time - start_time).seconds + ((new_time - start_time).microseconds / 1000000.0)


    def send_fly_relative_command(self, command_tuple, change_x, change_y, change_z, change_angle):
        """
        Send the packet to fly relative (this is Bebop only).

        :param command_tuple: command tuple per the parser
        :param change_x: change in x
        :param change_y: change in y
        :param change_z: change in z
        :param change_angle: change in angle
        """
        self.sequence_counter['SEND_WITH_ACK'] = (self.sequence_counter['SEND_WITH_ACK'] + 1) % 256
        packet = struct.pack("<BBBIBBHffff",
                             self.data_types_by_name['DATA_WITH_ACK'],
                             self.buffer_ids['SEND_WITH_ACK'],
                             self.sequence_counter['SEND_WITH_ACK'],
                             27,
                             command_tuple[0], command_tuple[1], command_tuple[2],
                             change_x, change_y, change_z, change_angle)

        self.safe_send(packet)

    def send_turn_command(self, command_tuple, degrees):
        """
        Build the packet for turning and send it

        :param command_tuple: command tuple from the parser
        :param degrees: how many degrees to turn
        :return: True if the command was sent and False otherwise
        """
        self.sequence_counter['SEND_WITH_ACK'] = (self.sequence_counter['SEND_WITH_ACK'] + 1) % 256

        packet = struct.pack("<BBBIBBHh",
                             self.data_types_by_name['DATA_WITH_ACK'],
                             self.buffer_ids['SEND_WITH_ACK'],
                             self.sequence_counter['SEND_WITH_ACK'],
                             13,
                             command_tuple[0], command_tuple[1], command_tuple[2],
                             degrees)

        return self.send_command_packet_ack(packet, self.sequence_counter['SEND_WITH_ACK'])


    def send_camera_move_command(self, command_tuple, pan, tilt):
        """
        Send the packet to move the camera (this is Bebop only).

        :param command_tuple: command tuple per the parser
        :param pan:
        :param tilt:
        """
        self.sequence_counter['SEND_WITH_ACK'] = (self.sequence_counter['SEND_WITH_ACK'] + 1) % 256
        packet = struct.pack("<BBBIBBHff",
                             self.data_types_by_name['DATA_WITH_ACK'],
                             self.buffer_ids['SEND_WITH_ACK'],
                             self.sequence_counter['SEND_WITH_ACK'],
                             19,
                             command_tuple[0], command_tuple[1], command_tuple[2],
                             pan, tilt)

        self.safe_send(packet)

    def send_enum_command_packet_ack(self, command_tuple, enum_value, usb_id=None):
        """
        Send a command on the ack channel with enum parameters as well (most likely a flip).
        All commandsandsensors except PCMD go on the ack channel per
        http://forum.developer.parrot.com/t/ble-characteristics-of-minidrones/5912/2

        the id of the last command sent (for use in ack) is the send counter (which is incremented before sending)

        :param command_tuple: 3 tuple of the command bytes.  0 padded for 4th byte
        :param enum_value: the enum index
        :return: nothing
        """
        self.sequence_counter['SEND_WITH_ACK'] = (self.sequence_counter['SEND_WITH_ACK'] + 1) % 256

        if (usb_id is None):
            packet = struct.pack("<BBBIBBHI", self.data_types_by_name['DATA_WITH_ACK'],
                                 self.buffer_ids['SEND_WITH_ACK'],
                                 self.sequence_counter['SEND_WITH_ACK'], 15,
                                 command_tuple[0], command_tuple[1], command_tuple[2],
                                 enum_value)
        else:
            packet = struct.pack("<BBBIBBHBI", self.data_types_by_name['DATA_WITH_ACK'],
                                 self.buffer_ids['SEND_WITH_ACK'],
                                 self.sequence_counter['SEND_WITH_ACK'], 16,
                                 command_tuple[0], command_tuple[1], command_tuple[2],
                                 usb_id, enum_value)
        return self.send_command_packet_ack(packet, self.sequence_counter['SEND_WITH_ACK'])

    def smart_sleep(self, timeout):
        """
        Sleeps the requested number of seconds but wakes up for notifications

        Note: time.sleep misbehaves for the BLE connections but seems ok for wifi.
        I encourage you to use smart_sleep since it handles the sleeping in a thread-safe way.

        :param timeout: number of seconds to sleep
        :return:
        """

        start_time = datetime.now()
        new_time = datetime.now()
        diff = (new_time - start_time).seconds + ((new_time - start_time).microseconds / 1000000.0)

        while (diff < timeout):
            time.sleep(0.1)
            new_time = datetime.now()
            diff = (new_time - start_time).seconds + ((new_time - start_time).microseconds / 1000000.0)

    def ack_packet(self, buffer_id, packet_id):
        """
        Ack the packet id specified by the argument on the ACK_COMMAND channel

        :param packet_id: the packet id to ack
        :return: nothing
        """
        #color_print("ack: buffer id of %d and packet id of %d" % (buffer_id, packet_id))
        new_buf_id = (buffer_id + 128) % 256

        if (new_buf_id not in self.sequence_counter):
            self.sequence_counter[new_buf_id] = 0
        else:
            self.sequence_counter[new_buf_id] = (self.sequence_counter[new_buf_id] + 1) % 256

        packet = struct.pack("<BBBIB", self.data_types_by_name['ACK'], new_buf_id,
                             self.sequence_counter[new_buf_id], 8,
                             packet_id)

        self.safe_send(packet)

