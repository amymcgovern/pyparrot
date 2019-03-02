"""
DroneVision is separated from the main Mambo/Bebop class to enable the use of the drone without the FPV camera.
If you want to do vision processing, you will need to create a DroneVision object to capture the
video stream.

Note that this module relies on the opencv module and the ffmpeg program

Ffmpeg write the images out to the images directory and then they are read in from the user thread.  The DroneVisionGUI
does not save copies of the images and instead shows you the images on the screen (they are saved to memory only).
While you can see the images in real-time from this program using VisionServer, if you need copies of the images,
you will want to use the ffmpeg approach.  If you want a smaller delay on your image data for real-time control, you likely want
to use libvlc and DroneVisionGUI.

Author: Amy McGovern, dramymcgovern@gmail.com
"""
import cv2
import threading
import time
import subprocess
import os
from os.path import join
import inspect
from pyparrot.utils.NonBlockingStreamReader import NonBlockingStreamReader
import shutil
import signal

class DroneVision:
    def __init__(self, drone_object, is_bebop, buffer_size=200, cleanup_old_images=True):
        """
        Setup your vision object and initialize your buffers.  You won't start seeing pictures
        until you call open_video.

        :param drone_object reference to the drone (mambo or bebop) object
        :param is_bebop: True if it is a bebop and false if it is a mambo
        :param buffer_size: number of frames to buffer in memory.  Defaults to 10.
        :param cleanup_old_images: clean up the old images in the directory (defaults to True, set to false to keep old data around)
        """
        self.fps = 30
        self.buffer_size = buffer_size
        self.drone_object = drone_object
        self.is_bebop = is_bebop
        self.cleanup_old_images = cleanup_old_images

        # initialize a buffer (will contain the last buffer_size vision objects)
        self.buffer = [None] * buffer_size
        self.buffer_index = 0

        # setup the thread for monitoring the vision (but don't start it until we connect in open_video)
        self.vision_thread = threading.Thread(target=self._buffer_vision,
                                              args=(buffer_size, ))
        self.user_vision_thread = None
        self.vision_running = True

        # the vision thread starts opencv on these files.  That will happen inside the other thread
        # so here we just sent the image index to 1 ( to start)
        self.image_index = 1


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


    def open_video(self):
        """
        Open the video stream using ffmpeg for capturing and processing.  The address for the stream
        is the same for all Mambos and is documented here:

        http://forum.developer.parrot.com/t/streaming-address-of-mambo-fpv-for-videoprojection/6442/6

        Remember that this will only work if you have connected to the wifi for your mambo!

        Note that the old method tried to open the stream directly into opencv but there are known issues
        with rtsp streams in opencv.  We bypassed opencv to use ffmpeg directly and then opencv is used to
        process the output of ffmpeg

        :return True if the vision opened correctly and False otherwise
        """

        # start the stream on the bebop
        if (self.is_bebop):
            self.drone_object.start_video_stream()

        # we have bypassed the old opencv VideoCapture method because it was unreliable for rtsp
        # get the path for the config files
        fullPath = inspect.getfile(DroneVision)
        shortPathIndex = fullPath.rfind("/")
        if (shortPathIndex == -1):
            # handle Windows paths
            shortPathIndex = fullPath.rfind("\\")
        print(shortPathIndex)
        shortPath = fullPath[0:shortPathIndex]
        self.imagePath = join(shortPath, "images")
        self.utilPath = join(shortPath, "utils")
        print(self.imagePath)
        print(self.utilPath)

        if (self.cleanup_old_images):
            print("removing all the old images")
            shutil.rmtree(self.imagePath)
            os.mkdir(self.imagePath)

        # the first step is to open the rtsp stream through ffmpeg first
        # this step creates a directory full of images, one per frame
        print("Opening ffmpeg")
        if (self.is_bebop):
            cmdStr = "ffmpeg -protocol_whitelist \"file,rtp,udp\" -i %s/bebop.sdp -r 30 image_" % self.utilPath + "%03d.png"
            print(cmdStr)
            self.ffmpeg_process = \
                subprocess.Popen(cmdStr, shell=True, cwd=self.imagePath, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        else:
            self.ffmpeg_process = \
                subprocess.Popen("ffmpeg -i rtsp://192.168.99.1/media/stream2 -r 30 image_%03d.png",
                               shell=True, cwd=self.imagePath, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        # immediately start the vision buffering (before we even know if it succeeded since waiting puts us behind)
        self._start_video_buffering()

        # open non-blocking readers to look for errors or success
        print("Opening non-blocking readers")
        stderr_reader = NonBlockingStreamReader(self.ffmpeg_process.stderr)
        stdout_reader = NonBlockingStreamReader(self.ffmpeg_process.stdout)


        # look for success in the stdout
        # If it starts correctly, it will have the following output in the stdout
        # Stream mapping:
        #   Stream #0:0 -> #0:0 (h264 (native) -> png (native))

        # if it fails, it has the following in stderr
        # Output file #0 does not contain any stream

        success = False
        while (not success):

            line = stderr_reader.readline()
            if (line is not None):
                line_str = line.decode("utf-8")
                print(line_str)
                if line_str.find("Stream #0:0 -> #0:0 (h264 (native) -> png (native))") > -1:
                    success = True
                    break
                if line_str.find("Output file #0 does not contain any stream") > -1:
                    print("Having trouble connecting to the camera 1.  A reboot of the mambo may help.")
                    break

            line = stdout_reader.readline()
            if (line is not None):
                line_str = line.decode("utf-8")
                print(line_str)
                if line_str.find("Output file #0 does not contain any stream") > -1:
                    print("Having trouble connecting to the camera 2.  A reboot of the mambo may help.")
                    break

                if line_str.find("Stream #0:0 -> #0:0 (h264 (native) -> png (native))") > -1:
                    success = True

        # cleanup our non-blocking readers no matter what happened
        stdout_reader.finish_reader()
        stderr_reader.finish_reader()

        # return whether or not it worked
        return success

    def _start_video_buffering(self):
        """
        If the video capture was successfully opened, then start the thread to buffer the stream

        :return: Nothing
        """
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

                #reset the bit for a new frame
                self.new_frame = False

            # put the thread back to sleep for fps
            # sleeping shorter to ensure we stay caught up on frames
            time.sleep(1.0 / (3.0 * self.fps))


    def _buffer_vision(self, buffer_size):
        """
        Internal method to save valid video captures from the camera fps times a second

        :param buffer_size: number of images to buffer (set in init)
        :return:
        """

        # start with no new data
        self.new_frame = False

        # when the method is first called, sometimes there is already data to catch up on
        # so find the latest image in the directory and set the index to that
        found_latest = False
        while (not found_latest):
            path = "%s/image_%03d.png" % (self.imagePath, self.image_index)
            if (os.path.exists(path)) and (not os.path.isfile(path)):
                # just increment through it (don't save any of these first images)
                self.image_index = self.image_index + 1
            else:
                found_latest = True

        # run forever, trying to grab the latest image
        while (self.vision_running):
            # grab the latest image from the ffmpeg stream
            try:
                # make the name for the next image
                path = "%s/image_%03d.png" % (self.imagePath, self.image_index)
                if (not os.path.exists(path)) and (not os.path.isfile(path)):
                    #print("File %s doesn't exist" % (path))
                    #print(os.listdir(self.imagePath))
                    continue

                img = cv2.imread(path,1)

                # sometimes cv2 returns a None object so skip putting those in the array
                if (img is not None):
                    self.image_index = self.image_index + 1

                    # got a new image, save it to the buffer directly
                    self.buffer_index += 1
                    self.buffer_index %= buffer_size
                    #print video_frame
                    self.buffer[self.buffer_index] = img
                    self.new_frame = True

            except cv2.error:
                #Assuming its an empty image, so decrement the index and try again.
                # print("Trying to read an empty png. Let's wait and try again.")
                self.image_index = self.image_index - 1
                continue

            # put the thread back to sleep for faster than fps to ensure we stay on top of the frames
            # coming in from ffmpeg
            time.sleep(1.0 / (2.0 * self.fps))
        

    def get_latest_valid_picture(self):
        """
        Return the latest valid image (from the buffer)

        :return: last valid image received from the Mambo
        """
        return self.buffer[self.buffer_index]

    def close_video(self):
        """
        Stop the vision processing and all its helper threads
        """

        # the helper threads look for this variable to be true
        self.vision_running = False

        # kill the ffmpeg subprocess
        print("Killing the ffmpeg subprocess")
        self.ffmpeg_process.kill()
        self.ffmpeg_process.terminate()
        time.sleep(3)

        if (self.ffmpeg_process.poll() is not None):
            print("Sending a second kill call to the ffmpeg process")
            self.ffmpeg_process.kill()
            self.ffmpeg_process.terminate()
            time.sleep(3)


        # send the command to kill the vision stream (bebop only)
        if (self.is_bebop):
            self.drone_object.stop_video_stream()

