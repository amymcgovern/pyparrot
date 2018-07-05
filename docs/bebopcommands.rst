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

``turn_degrees(degrees)`` Turns the bebop in place the specified number of degrees.
The range is -180 to 180.  This can be accomplished in direct_fly() as well but this one uses the
internal mambo sensors (which are not sent out right now) so it is more accurate.

``fly_direct(roll, pitch, yaw, vertical_movement, duration)`` Fly the bebop directly using the
specified roll, pitch, yaw, and vertical movements.  The commands are repeated for duration seconds.
Note there are currently no sensors reported back to the user to ensure that these are working but hopefully
that is addressed in a future firmware upgrade.  Each value ranges from -100 to 100.

``move_relative(dx, dy, dz, dradians)`` Moves the bebop a relative number of meters in x (forward/backward,
forward is positive), y (right/left, right is positive), dz (up/down, positive is down), and dradians.  DO NOT
USE THIS COMMAND YET.  While it correctly executes the command, it also randomly flies at high speed in random
directions after the command executes.  This seems to be a known bug in the forum.  DO NOT USE YET.

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

Sensor commands
^^^^^^^^^^^^^^^

``ask_for_state_update()`` This sends a request to the bebop to send back ALL states.  The data returns
fairly quickly although not instantly.  The bebop already has a sensor refresh rate of 10Hz but not all sensors are sent
automatically.  If you are looking for a specific sensor that is not automatically sent, you can call this but I don't
recommend sending it over and over.  Most of the sensors you need should be sent at either the 10Hz rate or as an event
is called that triggers that sensor.

``set_max_altitude(altitude)`` Set the maximum allowable altitude in meters

``set_max_tilt(tilt)`` Set the maximum allowable tilt in degrees for the drone (this limits speed).
The tilt must be between 5 (very slow) and 30 (very fast) degrees.

``set_max_tilt_rotation_speed(speed)`` Set the maximum allowable tilt rotation speed in degree/s.
The tilt rotation speed must be between 80 and 300 degree/s.

``set_max_vertical_speed(speed)`` Set the maximum allowable vertical speed in m/s.
The vertical speed must be between 0.5 and 2.5 m/s.

``set_max_rotation_speed(speed)`` Set the maximum allowable rotation speed in degree/s.
The rotation speed must be between 10 and 200 degree/s.

Bebop sensors
-------------

All of the sensor data that is passed back to the Bebop is saved in a python dictionary.
Since the Bebop code is still under active development, there will eventually be extra variables
saved outside of the dictionary.  The data is stored in the BebopSensors class.

The sensors are:

* flying_state: This is updated as frequently as the drone sends it out and can be one of "landed", "takingoff", "hovering", "flying", "landing", "emergency", "usertakeoff", "motor_ramping", "emergency_landing".  These are the values as specified in `ardrone3.xml <https://github.com/amymcgovern/pyparrot/blob/master/pyparrot/commandsandsensors/ardrone3.xml>`_.

* sensors_dict: all other sensors are saved by name in a dictionary.  The names come from the `ardrone3.xml <https://github.com/amymcgovern/pyparrot/blob/master/pyparrot/commandsandsensors/ardrone3.xml>`_ and `common.xml <https://github.com/amymcgovern/pyparrot/blob/master/pyparrot/commandsandsensors/common.xml>`_.

