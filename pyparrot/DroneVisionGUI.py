"""
DroneVisionGUI is a new class that parallels DroneVision but with several important changes.

1) This module uses VLC instead of FFMPEG
2) This module opens a GUI window to show you the video in real-time (you could
watch it in real-time previously through the VisionServer)
3) Because GUI windows are different on different OS's (and in particular OS X behaves differently
than linux and windows) and because they want to run in the main program thread, the way your program runs
is different.  You first open the GUI and then you have the GUI spawn a thread to run your program.
4) This module can use a virtual disk in memory to save the images, thus shortening the time delay for the
camera for your programs.

Author: Amy McGovern, dramymcgovern@gmail.com
Some of the LIBVLC code comes from
Author: Valentin Benke, valentin.benke@aon.at
"""
import cv2
import time
from functools import partial
from os.path import join
import inspect
import tempfile
import sys
import pyparrot.utils.vlc as vlc
from PyQt5.QtCore import Qt, QTimer, QThread
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QMainWindow, QWidget, QFrame, QSlider, QHBoxLayout, QPushButton, \
    QVBoxLayout, QAction, QFileDialog, QApplication


class Player(QMainWindow):
    """
    Modification of the simple Media Player using VLC and Qt
    to show the mambo stream

    The window part of this example was modified from the QT example cited below.
    VLC requires windows to create and show the video and this was a cross-platform solution.
    VLC will automatically create the windows in linux but not on the mac.
    Amy McGovern, dramymcgovern@gmail.com

    Qt example for VLC Python bindings
    https://github.com/devos50/vlc-pyqt5-example
    Copyright (C) 2009-2010 the VideoLAN team

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
    """
    def __init__(self, vlc_player, drone_gui):
        """
        Create a UI window for the VLC player
        :param vlc_player: the VLC player (created outside the function)
        """
        QMainWindow.__init__(self)
        self.setWindowTitle("VLC Drone Video Player")

        # save the media player
        self.mediaplayer = vlc_player

        # need a reference to the main drone vision class
        self.drone_vision = drone_gui

        # create the GUI
        self.createUI()

    def createUI(self):
        """
        Set up the window for the VLC viewer
        """
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)

        # In this widget, the video will be drawn
        if sys.platform == "darwin": # for MacOS
            from PyQt5.QtWidgets import QMacCocoaViewContainer
            self.videoframe = QMacCocoaViewContainer(0)
        else:
            self.videoframe = QFrame()
        self.palette = self.videoframe.palette()
        self.palette.setColor (QPalette.Window,
                               QColor(0,0,0))
        self.videoframe.setPalette(self.palette)
        self.videoframe.setAutoFillBackground(True)

        self.hbuttonbox = QHBoxLayout()
        self.playbutton = QPushButton("Run my program")
        self.hbuttonbox.addWidget(self.playbutton)
        self.playbutton.clicked.connect(partial(self.drone_vision.run_user_code, self.playbutton))

        self.landbutton = QPushButton("Land NOW")
        self.hbuttonbox.addWidget(self.landbutton)
        self.landbutton.clicked.connect(self.drone_vision.land)

        self.stopbutton = QPushButton("Quit")
        self.hbuttonbox.addWidget(self.stopbutton)
        self.stopbutton.clicked.connect(self.drone_vision.close_exit)

        self.vboxlayout = QVBoxLayout()
        self.vboxlayout.addWidget(self.videoframe)
        self.vboxlayout.addLayout(self.hbuttonbox)

        self.widget.setLayout(self.vboxlayout)

        # the media player has to be 'connected' to the QFrame
        # (otherwise a video would be displayed in it's own window)
        # this is platform specific!
        # you have to give the id of the QFrame (or similar object) to
        # vlc, different platforms have different functions for this
        if sys.platform.startswith('linux'): # for Linux using the X Server
            self.mediaplayer.set_xwindow(self.videoframe.winId())
        elif sys.platform == "win32": # for Windows
            self.mediaplayer.set_hwnd(self.videoframe.winId())
        elif sys.platform == "darwin": # for MacOS
            self.mediaplayer.set_nsobject(int(self.videoframe.winId()))


class UserVisionProcessingThread(QThread):

    def __init__(self, user_vision_function, user_args, drone_vision):
        """
        :param user_vision_function: user callback function to handle vision
        :param user_args: optional arguments to the user callback function
        """
        QThread.__init__(self)
        self.user_vision_function = user_vision_function
        self.user_args = user_args
        self.drone_vision = drone_vision

    def __del__(self):
        self.wait()

    def run(self):
        print("user callback being called")
        while (self.drone_vision.vision_running):
            self.user_vision_function(self.user_args)

            # put the thread back to sleep for fps
            # sleeping shorter to ensure we stay caught up on frames
            time.sleep(1.0 / (3.0 * self.drone_vision.fps))

        # exit when the vision thread ends
        print("exiting user vision thread")
        self.exit()

class UserCodeToRun(QThread):
    def __init__(self, user_function, user_args, drone_vision):
        """
        :param user_function: user code to run (presumably flies the drone)
        :param user_args: optional arguments to the user function
        """
        QThread.__init__(self)
        self.user_vision_function = user_function
        self.user_args = user_args
        self.drone_vision = drone_vision

    def __del__(self):
        self.wait()

    def run(self):
        self.user_vision_function(self.drone_vision, self.user_args)


class DroneVisionGUI:
    def __init__(self, drone_object, is_bebop, user_code_to_run, user_args, buffer_size=200, network_caching=200, fps=20):
        """
        Setup your vision object and initialize your buffers.  You won't start seeing pictures
        until you call open_video.

        :param drone_object reference to the drone (mambo or bebop) object
        :param is_bebop: True if it is a bebop and false if it is a mambo
        :param user_code_to_run: user code to run with the run button (remember
        this is needed due to the GUI taking the thread)
        :param user_args: arguments to the user code
        :param buffer_size: number of frames to buffer in memory.  Defaults to 10.
        :param network_caching: buffering time in milli-seconds, 200 should be enough, 150 works on some devices
        :param fps: frame rate for the vision
        """
        self.fps = fps
        self.vision_interval = int(1000 * 1.0 / self.fps)
        self.buffer_size = buffer_size
        self.drone_object = drone_object
        self.is_bebop = is_bebop

        # initialize a buffer (will contain the last buffer_size vision objects)
        self.buffer = [None] * buffer_size
        self.buffer_size = buffer_size
        self.buffer_index = 0

        # vision threading is done from a QTimer instead of a separate thread
        self.new_frame = False
        self.vision_running = True

        # the vision thread starts opencv on these files.  That will happen inside the other thread
        # so here we just sent the image index to 1 ( to start)
        self.image_index = 1

        # save the caching parameters and choice of libvlc
        self.network_caching = network_caching

        # save the user function and args for calling from the run button
        self.user_code_to_run = user_code_to_run
        self.user_args = user_args
        self.user_thread = UserCodeToRun(user_code_to_run, user_args, self)

        # in case we never setup a user callback function
        self.user_vision_thread = None

        # has the land button been clicked - saved in case the user needs it in their code
        self.land_button_clicked = False

    def run_user_code(self, button):
        """
        Start the thread to run the user code
        :return:
        """
        button.setEnabled(False)
        self.user_thread.start()


    def set_user_callback_function(self, user_callback_function=None, user_callback_args=None):
        """
        Set the (optional) user callback function for handling the new vision frames.  This is
        run in a separate thread that starts when you start the vision buffering

        :param user_callback_function: function
        :param user_callback_args: arguments to the function
        :return:
        """
        self.user_vision_thread = UserVisionProcessingThread(user_callback_function, user_callback_args, self)


    def open_video(self):
        """
        Open the video stream using vlc.  Note that this version is blocking meaning
        this function will NEVER return.  If you want to run your own code and not just
        watch the video, be sure you set your user code in the constructor!

        Remember that this will only work if you have connected to the wifi for your mambo!

        :return never returns due to QT running in the main loop by requirement
        """

        # start the stream on the bebop
        if (self.is_bebop):
            self.drone_object.start_video_stream()

        # we have bypassed the old opencv VideoCapture method because it was unreliable for rtsp

        # get the path for the config files
        fullPath = inspect.getfile(DroneVisionGUI)
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

        if self.is_bebop:
            # generate the streaming-address for the Bebop
            self.utilPath = join(shortPath, "utils")
            self.stream_adress = "%s/bebop.sdp" % self.utilPath
        else:
            # generate the streaming-address for the Mambo
            self.stream_adress = "rtsp://192.168.99.1/media/stream2"

        # initialise the vlc-player with the network-caching
        self.player = vlc.MediaPlayer(self.stream_adress, ":network-caching=" + str(self.network_caching))

        # start the buffering
        success = self._start_video_buffering()


    def _start_video_buffering(self):
        """
        If the video capture was successfully opened, then start the thread to buffer the stream

        :return: if using libvlc this will return whether or not the player started
        """
        # open/draw the GUI
        app = QApplication(sys.argv)
        self.vlc_gui = Player(vlc_player=self.player, drone_gui=self)
        self.vlc_gui.show()
        self.vlc_gui.resize(640, 480)

        # ensure that closing the window closes vision
        app.aboutToQuit.connect(self.land_close_exit)

        if (self.user_vision_thread is not None):
            print("Starting user vision thread")
            self.user_vision_thread.start()

        # setup the timer for snapshots
        self.timer = QTimer(self.vlc_gui)
        self.timer.setInterval(self.vision_interval)
        self.timer.timeout.connect(self._buffer_vision)
        self.timer.start()

        # show the stream
        success = self.player.play()
        print("success from play call is %s " % success)

        # start the GUI loop
        app.exec()


    def _buffer_vision(self):
        """
        Internal method to save valid video captures from the camera fps times a second

        :return:
        """

        # start with no new data
        self.new_frame = False

        # run forever, trying to grab the latest image
        if (self.vision_running):
            # generate a temporary file, gets deleted after usage automatically
            #self.file = tempfile.NamedTemporaryFile(dir=self.imagePath)
            self.file = join(self.imagePath, "visionStream.jpg")
            #self.file = tempfile.SpooledTemporaryFile(max_size=32768)
            # save the current picture from the stream
            self.player.video_take_snapshot(0, self.file, 0, 0)
            # read the picture into opencv
            img = cv2.imread(self.file)

            # sometimes cv2 returns a None object so skip putting those in the array
            if (img is not None):
                # got a new image, save it to the buffer directly
                self.buffer_index += 1
                self.buffer_index %= self.buffer_size
                #print video_frame
                self.buffer[self.buffer_index] = img
                self.new_frame = True

    def get_latest_valid_picture(self):
        """
        Return the latest valid image (from the buffer)

        :return: last valid image received from the Mambo
        """
        return self.buffer[self.buffer_index]

    def close_exit(self):
        """
        Land, close the video, and exit the GUI
        :return:
        """
        self.close_video()
        sys.exit()

    def land_close_exit(self):
        """
        Called if you Quit the GUI: lands the drone, stops vision, and exits the GUI
        :return:
        """
        self.land()
        self.close_exit()

    def land(self):
        """
        Send the land command over the emergency channel when the user pushes the button

        :return:
        """
        # tell the user that the land button was clicked
        self.land_button_clicked = True

        # land the drone
        if (self.is_bebop):
            if (not self.drone_object.is_landed()):
                self.drone_object.emergency_land()
        else:
            if (not self.drone_object.is_landed()):
                self.drone_object.safe_land(5)


    def close_video(self):
        """
        Stop the vision processing and all its helper threads
        """

        # the helper threads look for this variable to be true
        self.vision_running = False

        self.player.stop()

        # send the command to kill the vision stream (bebop only)
        if (self.is_bebop):
            self.drone_object.stop_video_stream()

