"""
MamboVision is separated from the main Mambo class to enable the use of the drone without the FPV camera.
If you want to do vision processing, you will need to create a MamboVision object to capture the
video stream.

Note that this module relies on the opencv module.

Author: Amy McGovern, dramymcgovern@gmail.com
"""
import cv2
import threading
import time

class MamboVision:
    def __init__(self, buffer_size=10):
        """
        Setup your vision object and initialize your buffers.  You won't start seeing pictures
        until you call open_video.

        :param buffer_size: number of frames to buffer in memory.  Defaults to 10.
        :param user_callback_function: callback function that will be called every time a new frame is available (optional)
        :param user_callback_args: arguments to the user callback function (optional)
        """
        self.fps = 30

        self.buffer_size = buffer_size

        # initialize a buffer (will contain the last buffer_size vision objects)
        self.buffer = [None] * buffer_size
        self.buffer_index = 0

        # setup the thread for monitoring the vision (but don't start it until we connect in open_video)
        self.vision_thread = threading.Thread(target=self._buffer_vision,
                                              args=(buffer_size, ))
        self.user_vision_thread = None
        self.vision_running = True

    def set_user_callback_function(self, user_callback_function=None, user_callback_args=None):
        """
        Set the (optional) user callback function for handling the new vision frames.  This is
        run in a separate thread that starts when you start the vision buffering

        :param user_callback_function: function
        :param user_callback_args: arguments to the function
        :return:
        """
        self.user_vision_thread = threading.Thread(target=self._user_callback,
                                                   args=(user_callback_function, user_callback_args))


    def open_video(self, max_retries=3):
        """
        Open the video stream in opencv for capturing and processing.  The address for the stream
        is the same for all Mambos and is documented here:

        http://forum.developer.parrot.com/t/streaming-address-of-mambo-fpv-for-videoprojection/6442/6

        Remember that this will only work if you have connected to the wifi for your mambo!

        :param max_retries: Maximum number of retries in opening the camera (remember to connect to camera wifi!).
        Defaults to 3.

        :return True if the vision opened correctly and False otherwise
        """
        print("opening the camera")
        self.capture = cv2.VideoCapture("rtsp://192.168.99.1/media/stream2")

        # if you do 0, it opens the laptop webcam
        #self.capture = cv2.VideoCapture(0)

        # if it didn't open the first time, try again a maximum number of times
        try_num = 1
        while (not self.capture.isOpened() and try_num < max_retries):
            print("re-trying to open the capture")
            self.capture = cv2.VideoCapture("rtsp://192.168.99.1/media/stream2")
            try_num += 1

        # return whether the vision opened
        return self.capture.isOpened()

    def start_video_buffering(self):
        """
        If the video capture was successfully opened, then start the thread to buffer the stream

        :return:
        """
        if (self.capture.isOpened()):
            print("starting vision thread")
            self.vision_thread.start()

            if (self.user_vision_thread is not None):
                self.user_vision_thread.start()

    def _user_callback(self, user_vision_function, user_args):
        """
        Internal method to call the user vision functions

        :param user_vision_function: user callback function to handle vision
        :param user_args: optional arguments to the user callback function
        :return:
        """

        while (self.vision_running):
            if (self.new_frame):
                user_vision_function(user_args)

            # put the thread back to sleep for fps
            time.sleep(1.0 / self.fps)


    def _buffer_vision(self, buffer_size):
        """
        Internal method to save valid video captures from the camera fps times a second

        :param buffer_size: number of images to buffer (set in init)
        :return:
        """

        while (self.vision_running):
            #reset the bit
            self.new_frame = False

            # grab the latest image
            capture_correct, video_frame = self.capture.read()
            if (capture_correct):
                self.buffer_index += 1
                self.buffer_index %= buffer_size
                #print video_frame
                self.buffer[self.buffer_index] = video_frame
                self.new_frame = True

            # put the thread back to sleep for fps
            time.sleep(1.0 / self.fps)
        

    def get_latest_valid_picture(self):
        """
        Return the latest valid image (from the buffer)

        :return: last valid image received from the Mambo
        """
        return self.buffer[self.buffer_index]

    def stop_vision_buffering(self):
        """
        Should stop the vision thread
        """
        self.vision_running = False
    
