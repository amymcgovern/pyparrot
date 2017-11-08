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

    def __init__(self, drone_type="Bebop"):
        """
        Can be a connection to a Bebop or a Mambo right now

        :param type: type of drone to connect to
        """
        self.is_connected = False
        if (drone_type not in ("Bebop", "Mambo")):
            color_print("Error: only type Bebop and Mambo are currently supported", "ERROR")
            return

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

        self.frame_counter = {
            'SEND_NO_ACK': 0,
            'SEND_WITH_ACK': 0,
            'SEND_HIGH_PRIORITY': 0,
            'ACK_COMMAND': 0,
            'RECEIVE_WITH_ACK': 0
        }

        self.send_buffer_ids = {
            'SEND_NO_ACK': 10,           # not-ack commandsandsensors (piloting and camera rotations)
            'SEND_WITH_ACK': 11,         # ack commandsandsensors (all piloting commandsandsensors)
            'SEND_HIGH_PRIORITY': 12,    # emergency commandsandsensors
            'VIDEO_ACK': 13              # ack for video
        }

        self.receive_buffer_ids = {
            '127' : 'ACK_DRONE_DATA',        # drone data that needs an ack
            '126' : 'NO_ACK_DRONE_DATA',     # data from drone (including battery and others), no ack
            '125' : 'VIDEO_DATA',            # video data
            }


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
            time.sleep(0.5)
            num_tries += 1

        # if we didn't hear the listener, return False
        if (not self.is_connected):
            color_print("connection failed: did you remember to connect your machine to the Drone's wifi network?", "ERROR")
            return False

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
            (packet_type, packet_id, packet_seq_id, packet_size) = struct.unpack('<BBBI', my_data[0:7])
            recv_data = data[7:packet_size]

            self.handle_frame(packet_type, packet_id, packet_seq_id, recv_data)

            # loop in case there is more data
            my_data = my_data[packet_size:]

    def handle_frame(self, packet_type, packet_id, packet_seq_id, recv_data):
        if (self.data_types_by_number[packet_type] == 'ACK'):
            pass
        elif (self.data_types_by_number[packet_type] == 'DATA_NO_ACK'):
            pass
        elif (self.data_types_by_number[packet_type] == 'LOW_LATENCY_DATA'):
            pass
        elif (self.data_types_by_number[packet_type] == 'DATA_WITH_ACK'):
            self.mambo.update_sensors(data, ack=True)



        print "got a packet type of of %d " % packet_type
        print "got a packet id of of %d " % packet_id
        print "got a packet seq id of of %d " % packet_seq_id


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
        self.udp_send_sock.connect((self.drone_ip, self.udp_send_port))

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


    def send_noparam_command_packet_ack(self, command_tuple):
        self.frame_counter['SEND_WITH_ACK'] = (self.frame_counter['SEND_WITH_ACK'] + 1) % 256
        print (self.data_types_by_name['DATA_WITH_ACK'], self.send_buffer_ids['SEND_WITH_ACK'],
               self.frame_counter['SEND_WITH_ACK'], 0, 0, 0, 11,
               command_tuple[0], command_tuple[1], command_tuple[2], 0)
        packet = struct.pack("<BBBBBBBBBBB", self.data_types_by_name['DATA_WITH_ACK'], self.send_buffer_ids['SEND_WITH_ACK'],
                             self.frame_counter['SEND_WITH_ACK'], 11, 0, 0, 0,
                             command_tuple[0], command_tuple[1], command_tuple[2], 0)
        self.udp_send_sock.send(packet)

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