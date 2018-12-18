.. title:: Bebop Commands and Sensors

.. bebopcommands:

Bebop Commands and Sensors
==============================

Bebop commands
--------------

Each of the public commands available to control the bebop is listed below with its documentation.
The code is also well documented and you can also look at the API through readthedocs.
All of the functions preceeded with an underscore are intended to be internal functions and are not listed below.

Creating a Bebop object
^^^^^^^^^^^^^^^^^^^^^^^

``Bebop(drone_type="Bebop2")`` create a Bebop object with an optional drone_type argument that can be used to create
a bebop one or bebop 2 object.  Default is Bebop 2.  Note, there is limited support for the original bebop since
I do not own one for testing.

Connecting and disconnecting
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``connect(num_retries)`` connect to the Bebop's wifi services.  This performs a handshake.
This can take several seconds to ensure the connection is working.
You can specify a maximum number of re-tries.  Returns true if the connection suceeded or False otherwise.

``disconnect()`` disconnect from the wifi connection

Takeoff and landing
^^^^^^^^^^^^^^^^^^^

``takeoff()`` Sends a single takeoff command to the bebop.  This is not the recommended method.

``safe_takeoff(timeout)`` This is the recommended method for takeoff.  It sends a command and then checks the
sensors (via flying state) to ensure the bebop is actually taking off.  Then it waits until the bebop is
flying or hovering to return.  It will timeout and return if the time exceeds timeout seconds.

``land()`` Sends a single land command to the bebop.  This is not the recommended method.

``safe_land(timeout)`` This is the recommended method to land the bebop.  Sends commands
until the bebop has actually reached the landed state. It will timeout and return if the time exceeds timeout seconds.

Flying
^^^^^^

``flip(direction)`` Sends the flip command to the bebop. Valid directions to flip are: front, back, right, left.

``fly_direct(roll, pitch, yaw, vertical_movement, duration)`` Fly the bebop directly using the
specified roll, pitch, yaw, and vertical movements.  The commands are repeated for duration seconds.
Note there are currently no sensors reported back to the user to ensure that these are working but hopefully
that is addressed in a future firmware upgrade.  Each value ranges from -100 to 100 and is essentially a percentage
and direction of the max_tilt (for roll/pitch) or max_vertical_speed (for vertical movement).

``move_relative(dx, dy, dz, dradians)`` Moves the bebop a relative number of meters in x (forward/backward,
forward is positive), y (right/left, right is positive), dz (up/down, positive is down), and dradians.
If you use this command INDOORS, make sure you either have FULL GPS coverage or NO GPS coverage (e.g. cover the front of the bebop
 with tin foil to keep it from getting a lock).  If it has mixed coverage, it randomly flies at high speed in random
directions after the command executes.  This is a known issue in Parrot's firmware and they state that a fix is coming.

``set_max_altitude(altitude)`` Set the maximum allowable altitude in meters.
The altitude must be between 0.5 and 150 meters.

``set_max_distance(distance)`` Set max distance between the takeoff and the drone in meters.
The distance must be between 10 and 2000 meters.

``enable_geofence(value)`` If geofence is enabled, the drone won't fly over the given max distance.
Valid value: 1 if the drone can't fly further than max distance, 0 if no limitation on the drone should be done.

``set_max_tilt(tilt)`` Set the maximum allowable tilt in degrees for the drone (this limits speed).
The tilt must be between 5 (very slow) and 30 (very fast) degrees.

``set_max_tilt_rotation_speed(speed)`` Set the maximum allowable tilt rotation speed in degree/s.
The tilt rotation speed must be between 80 and 300 degree/s.

``set_max_vertical_speed(speed)`` Set the maximum allowable vertical speed in m/s.
The vertical speed must be between 0.5 and 2.5 m/s.

``set_max_rotation_speed(speed)`` Set the maximum allowable rotation speed in degree/s.
The rotation speed must be between 10 and 200 degree/s.

``set_flat_trim(duration=0)`` Tell the Bebop to run with a flat trim.  If duration > 0, waits for the comand to be acknowledged

``set_hull_protection(present)`` Set the presence of hull protection (only for bebop 1).
The value must be 1 if hull protection is present or 0 if not present.  This is only useful for the bebop 1.

``set_indoor(is_outdoor)`` Set the bebop 1 (ignored on bebop 2) to indoor or outdoor mode.
The value must be 1 if bebop 1 is outdoors or 0 if it is indoors.  This is only useful for the bebop 1.

Pausing or sleeping in a thread safe manner
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``smart_sleep(seconds)``  This sleeps the number of seconds (which can be a floating point) but wakes for all
wifi notifications. You should use this instead of time.sleep to be consistent with the mambo but it is not
required (whereas time.sleep() will break a mambo using BLE).

Video camera
^^^^^^^^^^^^

``start_video_stream()``: tells the bebop to start streaming the video.  These are really intended to be
called within the DroneVision or DroneVisionGUI functions and not directly by the user (but you can call
them directly if you are writing your own vision routines).

``stop_video_stream()``: tells the bebop to stop streaming the video.  Same as above: intended to be called
by the DroneVision or DroneVisionGUI routines.

``set_video_stream_mode(mode)``: set the video mode to one of three choices: "low_latency",
"high_reliability", "high_reliability_low_framerate".  low_latency is the default.

``pan_tilt_camera(tilt_degrees, pan_degrees)``: Send the command to pan/tilt the camera by the specified number of degrees in pan/tilt.
Note, this only seems to work in small increments.  Use pan_tilt_velocity to get the camera to look straight downward.

``pan_tilt_camera_velocity(self, tilt_velocity, pan_velocity, duration=0)``: Send the command to tilt the camera by
the specified number of degrees per second in pan/tilt. This function has two modes.  First, if duration is 0,
the initial velocity is sent and then the function returns (meaning the camera will keep moving).
If duration is greater than 0, the command executes for that amount of time and then sends a stop command to
the camera and then returns.

``set_picture_format(format)``: Change the picture format to raw, jpeg, snapshot or jpeg_fisheye.

``set_white_balance(type)``: Change the type of white balance between: auto, tungsten, daylight, cloudy or cool_white.

``set_exposition(value)``: Change the image exposition between -1.5 and 1.5.

``set_saturation(value)``: Change the image saturation between -100 and 100.

``set_timelapse(enable, interval)``: To start a timelapse set enable at 1 and an interval between 8 and 300 sec.
To stop the  timelapse just set enable to 0.

``set_video_stabilization(mode)``: Change the video stabilization between 4 modes: roll_pitch, pitch, roll, none.

``set_video_recording(mode)``: Change the video recording mode between quality and time.

``set_video_framerate(framerate)``: Change the video framerate between: 24_FPS, 25_FPS or 30_FPS.

``set_video_resolutions(type)``: Change the video resolutions for stream and rec between rec1080_stream480, rec720_stream720.

Sensor commands
^^^^^^^^^^^^^^^

``ask_for_state_update()`` This sends a request to the bebop to send back ALL states.  The data returns
fairly quickly although not instantly.  The bebop already has a sensor refresh rate of 10Hz but not all sensors are sent
automatically.  If you are looking for a specific sensor that is not automatically sent, you can call this but I don't
recommend sending it over and over.  Most of the sensors you need should be sent at either the 10Hz rate or as an event
is called that triggers that sensor.

Bebop sensors
-------------

All of the sensor data that is passed back to the Bebop is saved in a python dictionary.  As needed, other variables
are stored outside the dictionary but you can get everything you need from the dictionary itself.  All of the data
is stored in the BebopSensors class.

The easiest way to interact with the sensors is to call:

``bebop.set_user_sensor_callback(function, args)``. This sets a user callback function with optional
arguments that is called each time a sensor is updated.  The refresh rate on wifi is 10Hz.

The sensors are:

* battery (defaults to 100 and stays at that level until a real reading is received from the drone)
* flying_state: This is updated as frequently as the drone sends it out and can be one of "landed", "takingoff", "hovering", "flying", "landing", "emergency", "usertakeoff", "motor_ramping", "emergency_landing".  These are the values as specified in `ardrone3.xml <https://github.com/amymcgovern/pyparrot/blob/master/pyparrot/commandsandsensors/ardrone3.xml>`_.
* sensors_dict: all other sensors are saved by name in a dictionary.  The names come from the `ardrone3.xml <https://github.com/amymcgovern/pyparrot/blob/master/pyparrot/commandsandsensors/ardrone3.xml>`_ and `common.xml <https://github.com/amymcgovern/pyparrot/blob/master/pyparrot/commandsandsensors/common.xml>`_.
