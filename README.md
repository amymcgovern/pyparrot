# pyparrot
Python interface for Parrot Drones

pyparrot was designed and implemented by Dr. Amy McGovern to program Parrot Mambo and Parrot Bebop 2
drones using python.  This interface was developed to teach K-20 STEM concepts
(programming, math, and more) by programming a drone to fly autonomously.
Anyone can use it who is interested in autonomous drone programming!

# Installation, Quick-start, Documentation, FAQs

Extensive documentation is available at [https://pyparrot.readthedocs.io](https://pyparrot.readthedocs.io)

# Major updates and releases:
* 8/30/2018: Version 1.5.2: Updated camera pan_tilt for Bebop 1 (thanks Victor804)
* 8/21/2018: Version 1.5.1: fixed small fix for typo in minidrones (for swing)
* 8/18/2018: Version 1.5.0: major update to suppport parrot swing drones (thank you Victor804).  This does break a small backwards compatibility in that you need to import Mambo from Minidrone instead of Mambo.  Everything else remains the same.
* 8/9/2018: Version 1.4.31: hard-coded name for vision stream on windows
* 8/9/2018: Version 1.4.30: fixed vision bug in windows using VLC (tempfile issues) and also made fps a parameter for VLC vision
* 7/16/2018: Version 1.4.29: added bebop user sensor callback function to match mambo
* 7/15/2018: Version 1.4.28: added bebop battery state to default state variables (was in the dictionary only before)
* 7/13/2018: Version 1.4.27: updated Mambo() initialization to not require address for wifi mode and also updated groundcam demo for Mambo
* 7/12/2018: Version 1.4.26: added new Bebop commands (mostly setting max limits for the bebop)
* 7/11/2018: Version 1.4.25: fixed groundcam pictures for Mambo
* 7/8/2018: Version 1.4.24: switched tempfile to back to NamedTemporaryFile in DroneVisionGUI due to OS incompatibilities
* 7/8/2018: Version 1.4.23: switched tempfile to SpooledTemporaryFile in DroneVisionGUI to make it faster (uses memory instead of disk)
* 7/6/2018: Version 1.4.22: Added a wait in flat_trim for Bebop until it is received (optional)
* 7/5/2018: Version 1.4.21: Added max_tilt and max_altitude to the Bebop commands.
* 7/4/2018: Version 1.4.20: While move_relative is implemented, it seems to have a firmware bug so DO NOT USE.
* 7/4/2018: Version 1.4.19: Added move_relative command to the Bebop API.  For now, only dx, dy, and dradians should be used as there seems to be a bug internal to the firmware on dz.
* 6/17/2018: Version 1.4.18 Added landed button status to the Drone Vision GUI for safety in user code
* 6/16/2018: Version 1.4.17 Added flat trim to mambo also
* 6/16/2018: Version 1.4.16 Added flat trim to bebop
* 6/15/2018: Version 1.4.15 Removed a stray print, updated documentation, cast turn_degrees arguments to an int in Mambo.
* 6/11/2018: Version 1.4.14 Added bebop sdp file to the release on pip
* 6/7/2018: Version 1.4.13 Fixed duration in PCMD to use milliseconds instead of integer seconds
* 6/7/2018: Version 1.4.12 Added an option to fly_direct to allow the command to be sent once
* 6/6/2018: Version 1.4.11 Fixed a stray import statment not fixed from the move to pip
* 5/31/2018: Version 1.4.10 Documentation updated significantly and moved to readthedocs
* 5/30/2018: Version 1.4.7 and 1.4.8 and 1.4.9 fixed scripts location to release find_mambo script and added readthedocs documents
* 5/29/2018: Version 1.4.6 Accepted fixes for Bebop 1 compatibility
* 5/28/2018: Version 1.4.5 Fixed imports for new pypi structure and added xml files to pypi.
* 5/25/2018: Version 1.4.3. Uploaded to pypi so pyparrot can now be installed directory from pip.  Updated documentation for new vision.
* 5/23/2018: Updated function (contributed) to download pictures from Mambo's downward facing camera. 
* 3/25/2018: Added DroneVisionGUI which is a version of the vision that shows the video stream (for Bebop or Mambo) in real time.
* 2/22/2018: Version 1.3.2.  Updated DroneVision to make the vision processing faster.  Interface changed to only have the user call open_vision and close_vision (and not start_video_buffering)
* 2/10/2018: Version 1.3.1. Updated DroneVision to work on Windows.
* 2/8/2018: Version 1.3. Vision is working for both the Mambo and Bebop in a general interface called DroneVision.  Major documenation updates as well.
* 2/6/2018: Updated Mambo to add speed settings for tilt & vertical.  Needed for class.
* 2/4/2018: Unofficial updates to add ffmpeg support to the vision (will make an official release with examples soon)
* 12/09/2017: Version 1.2.  Mambo now gives estimated orientation using quaternions.  Bebop now streams vision, which is accessible via VLC or other video clients.  Coming soon: opencv hooks into the vision.  
* 12/02/2017: Version 1.1.  Fixed sensors with multiple values for Mambo and Bebop.
* 11/26/2017: Initial release, version 1.0.  Working wifi and BLE for Mambo, initial flight for Bebop.

# Programming and using your drones responsibly

It is your job to program and use your drones responsibly!  We are not responsible for any losses or damages of your drones or injuries.  Please fly safely and obey all laws.

