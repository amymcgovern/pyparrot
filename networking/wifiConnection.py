"""
Holds all the data and commands needed to fly a Bebop drone.

Author: Amy McGovern, dramymcgovern@gmail.com
"""

from zeroconf import ServiceBrowser, Zeroconf
import time
import socket
import ipaddress
import json
from utils.colorPrint import color_print
import struct
from threading import Thread

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

    def __init__(self, drone, drone_type="Bebop"):
        """
        Can be a connection to a Bebop or a Mambo right now

        :param type: type of drone to connect to
        """
        self.is_connected = False
        if (drone_type not in ("Bebop", "Mambo")):
            color_print("Error: only type Bebop and Mambo are currently supported", "ERROR")
            return

        self.drone = drone

        self.drone_type = drone_type
        self.udp_send_port = 0 # defined during the handshake
        self.udp_receive_port = 43210
        self.is_listening = True  # for the UDP listener

        if (drone_type == "Bebop"):
            self.mdns_address = "_arsdk-090c._udp.local."
        elif (drone_type == "Mambo"):
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
            'SEND_NO_ACK': 0,
            'SEND_WITH_ACK': 0,
            'SEND_HIGH_PRIORITY': 0,
            'VIDEO_ACK': 0,
            'ACK_DRONE_DATA': 0,
            'NO_ACK_DRONE_DATA': 0,
            'VIDEO_DATA': 0,
        }

        self.buffer_ids = {
            'SEND_NO_ACK': 10,           # not-ack commandsandsensors (piloting and camera rotations)
            'SEND_WITH_ACK': 11,         # ack commandsandsensors (all piloting commandsandsensors)
            'SEND_HIGH_PRIORITY': 12,    # emergency commandsandsensors
            'VIDEO_ACK': 13,               # ack for video
            'ACK_DRONE_DATA' : 127,        # drone data that needs an ack
            'NO_ACK_DRONE_DATA' : 126,     # data from drone (including battery and others), no ack
            'VIDEO_DATA' : 125,            # video data
            'ACK_FROM_SEND_WITH_ACK': 139  # 128 + buffer id for 'SEND_WITH_ACK' is 139
            }

        # store whether a command was acked
        self.command_received = {
            'SEND_WITH_ACK': False,
            'SEND_HIGH_PRIORITY': False,
            'ACK_COMMAND': False
        }

        # maximum number of times to try a packet before assuming it failed
        self.max_packet_retries = 1


    def connect(self, num_retries):
        """
        Connects to the drone

        :param num_retries: maximum number of retries

        :return: True if the connection suceeded and False otherwise
        """

        zeroconf = Zeroconf()
        listener = mDNSListener(self)

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
            self.listener_thread = Thread(target=self._listen_socket)
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

        sleep_timer = 0.3
        while (self.is_listening):
            try:
                data = self.udp_receive_sock.recv(66000)
                if len(data) > 0:
                    self.handle_data(data)
                    #print "listening got data"
                    #print data

            except socket.timeout:
                time.sleep(sleep_timer)

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
            print "inside loop to handle data "
            (packet_type, buffer_id, packet_seq_id, packet_size) = struct.unpack('<BBBI', my_data[0:7])
            recv_data = data[7:packet_size]

            self.handle_frame(packet_type, buffer_id, packet_seq_id, recv_data)

            # loop in case there is more data
            my_data = my_data[packet_size:]

    def handle_frame(self, packet_type, buffer_id, packet_seq_id, recv_data):
        print "got a packet type of of %d " % packet_type
        print "got a buffer id of of %d " % buffer_id
        print "got a packet seq id of of %d " % packet_seq_id

        if (self.data_types_by_number[packet_type] == 'ACK'):
            print "setting command received to true"
            ack_seq = int(struct.unpack("<B", recv_data)[0])
            self._set_command_received('SEND_WITH_ACK', True, ack_seq)
            self.ack_packet(ack_seq)
        elif (self.data_types_by_number[packet_type] == 'DATA_NO_ACK'):
            self.drone.update_sensors(packet_type, packet_seq_id, recv_data, ack=False)
        elif (self.data_types_by_number[packet_type] == 'LOW_LATENCY_DATA'):
            print "Need to handle Low latency data"
        elif (self.data_types_by_number[packet_type] == 'DATA_WITH_ACK'):
            self.drone.update_sensors(packet_type, packet_seq_id, recv_data, ack=True)
        else:
            color_print("HELP ME", "ERROR")
            print "got a different type of data - help"



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
        #print ipaddress.IPv4Address(self.connection_info.address)
        self.drone_ip = ipaddress.IPv4Address(self.connection_info.address).exploded

        # connect
        tcp_sock.connect((self.drone_ip, self.connection_info.port))

        # send the handshake information
        json_string = json.dumps({ "d2c_port":self.udp_receive_port, "controller_type":"computer", "controller_name":"pyparrot" })
        print json_string
        tcp_sock.send(json_string)

        # wait for the response
        finished = False
        num_try = 0
        while (not finished and num_try < num_retries):
            data = tcp_sock.recv(4096)
            if (len(data) > 0):
                my_data = data[0:-1]
                self.udp_data = json.loads(str(my_data))

                # if the drone refuses the connection, return false
                if (self.udp_data['status'] != 0):
                    return False

                print self.udp_data
                self.udp_send_port = self.udp_data['c2d_port']
                print "c2d_port is %d" % self.udp_send_port
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
        self.udp_send_sock.close()
        self.udp_receive_sock.close()

    def safe_send(self, packet):

        packet_sent = False
        print "inside safe send"

        while (not packet_sent):
            try:
                self.udp_send_sock.sendto(packet, (self.drone_ip, self.udp_send_port))
                packet_sent = True
            except:
                print "resetting connection"
                self.udp_send_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
                self.udp_send_sock.connect((self.drone_ip, self.udp_send_port))


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

    def send_noparam_command_packet_ack(self, command_tuple):
        self.sequence_counter['SEND_WITH_ACK'] = (self.sequence_counter['SEND_WITH_ACK'] + 1) % 256

        packet = struct.pack("<BBBIBBH", self.data_types_by_name['DATA_WITH_ACK'],
                             self.buffer_ids['SEND_WITH_ACK'],
                             self.sequence_counter['SEND_WITH_ACK'], 10,
                             command_tuple[0], command_tuple[1], command_tuple[2])

        print (self.data_types_by_name['DATA_WITH_ACK'], self.buffer_ids['SEND_WITH_ACK'],
               self.sequence_counter['SEND_WITH_ACK'], 11,
               command_tuple[0], command_tuple[1], command_tuple[2], 0)
        self.send_command_packet_ack(packet, self.sequence_counter['SEND_WITH_ACK'])

        #self.safe_send(packet)

    def smart_sleep(self, timeout):
        """
        Sleeps the requested number of seconds but wakes up for notifications

        Note: NEVER use regular time.sleep!  It is a blocking sleep and it will likely
        cause the WIFI to disconnect due to dropped notifications.  Always use smart_sleep instead!

        :param timeout: number of seconds to sleep
        :return:
        """

        start_time = time.time()
        while (time.time() - start_time < timeout):
            time.sleep(0.1)

    def ack_packet(self, packet_id):
        """
        Ack the packet id specified by the argument on the ACK_COMMAND channel

        :param packet_id: the packet id to ack
        :return: nothing
        """
        color_print("ack last packet on the ACK_COMMAND channel", "INFO")
        self.sequence_counter['ACK_DRONE_DATA'] = (self.sequence_counter['ACK_DRONE_DATA'] + 1) % 256
        packet = struct.pack("<BBBIB", self.data_types_by_name['ACK'], self.buffer_ids['ACK_DRONE_DATA'],
                             self.sequence_counter['ACK_DRONE_DATA'], 8,
                             packet_id)
        print (self.data_types_by_name['ACK'], self.buffer_ids['ACK_DRONE_DATA'],
               self.sequence_counter['ACK_DRONE_DATA'], 8,
               packet_id)

        self.safe_send(packet)