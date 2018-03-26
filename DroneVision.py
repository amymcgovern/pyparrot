"""
DroneVision is separated from the main Mambo/Bebop class to enable the use of the drone without the FPV camera.
If you want to do vision processing, you will need to create a DroneVision object to capture the
video stream.

Note that this module relies on the opencv module and the libvlc module

Author: Valentin Benke, valentin.benke@aon.at
Based on: pyparrot by Amy McGovern, dramymcgovern@gmail.com
"""
import cv2
import Drohne.Mambo.libvlc as libvlc
import tempfile
import inspect
from os.path import join


class DroneVision:
    def __init__(self, drone_object, is_bebop, network_caching=200):
        '''
        Prepare everything for the start of the stream

        :param drone_object: reference to the drone (mambo or bebop) object, if it's a Mambo you can also use None
        :param is_bebop: True if it is a bebop and False if it is a mambo
        :param network_caching: buffering time in milli-seconds, 200 should be enough, 150 works on some devices
        '''
        self.drone_object = drone_object
        self.is_bebop = is_bebop
        self.network_caching = network_caching

        fullPath = inspect.getfile(DroneVision)
        shortPathIndex = fullPath.rfind("/")
        if (shortPathIndex == -1):
            # handle Windows paths
            shortPathIndex = fullPath.rfind("\\")
        print(shortPathIndex)
        shortPath = fullPath[0:shortPathIndex]
        if self.is_bebop: #generate the streaming-address for the Bebop
            self.utilPath = join(shortPath, "utils")
            self.stream_adress = "%s/bebop.sdp" % self.utilPath
        else: #generate the streaming-address for the Mambo
            self.stream_adress = "rtsp://192.168.99.1/media/stream2"

        #initialise the vlc-player with the network-caching
        self.player = libvlc.MediaPlayer(self.stream_adress,":network-caching="+str(self.network_caching))


    def open_video(self):
        '''
        starts the video stream from the drone
        :return: if -1 it couldn't open the stream
        '''

        #start the stream from the Bebop
        if (self.is_bebop):
            self.drone_object.start_video_stream()
        self.success = self.player.play()
        if self.success == -1:
            print "Failed to open stream"
        return self.success


    def get_latest_valid_picture(self):
        '''
        get the latest frame
        :return: a frame ready to use in opencv
        '''

        #generate a temporary file, gets deleted after usage automatically
        self.file = tempfile.NamedTemporaryFile()
        #save the current picture from the stream
        self.player.video_take_snapshot(0, self.file.name, 0, 0)
        #read the picture into opencv
        return cv2.imread(self.file.name)


    def close_video(self):
        '''
        just closes the video transmission
        :return:
        '''
        self.player.stop()

