.. title:: Minidrone Commands and Sensors

.. minidronecommands:

Minidrone Commands and Sensors
==============================

Minidrone commands
--------------

Each of the public commands available to control the minidrone is listed below with its documentation.
The code is also well documented and you can also look at the API through readthedocs.
All of the functions preceeded with an underscore are intended to be internal functions and are not listed below.

Creating a Mambo object
^^^^^^^^^^^^^^^^^^^^^^^

``Mambo(address="", use_wifi=True/False)``
create a mambo object with the specific harware address (found using findMinidrone). The use_wifi argument defaults to
False (which means BLE is the default).  Set to True to use wifi. You can only use wifi if you have a FPV camera
installed on your Mambo!  If you are using wifi, the hardware address argument can be ignored (it defaults to an empty
string).

Creating a Swing object
^^^^^^^^^^^^^^^^^^^^^^^

``Swing(address="")``
create a Swing object with the specific harware address (found using findMinidrone).

Connecting and disconnecting
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``connect(num_retries)`` connect to the Minidrone either using BLE services and characteristics or wifi
(specified when you created the Mambo object).  This can take several seconds to ensure the connection is working.
You can specify a maximum number of re-tries.  Returns true if the connection suceeded or False otherwise.

``disconnect()`` disconnect from the BLE or wifi connection

Takeoff and landing
^^^^^^^^^^^^^^^^^^^

``safe_takeoff(timeout)`` This is the recommended method for takeoff.  It sends a command and then checks the
sensors (via flying state) to ensure the minidrone is actually taking off.  Then it waits until the minidrone is
flying or hovering to return.  It will timeout and return if the time exceeds timeout seconds.

``safe_land(timeout)`` This is the recommended method to land the minidrone.  Sends commands
until the minidrone has actually reached the landed state. It will timeout and return if the time exceeds timeout seconds.

``takeoff()`` Sends a single takeoff command to the minidrone.  This is not the recommended method.

``land()`` Sends a single land command to the minidrone.  This is not the recommended method.

``turn_on_auto_takeoff()`` This puts the minidrone in throw mode.  When it is in throw mode, the eyes will blink.

Flying
^^^^^^

``hover()`` and ``set_flat_trim()`` both tell the drone to assume the current configuration is a flat trim and it will
use this as the default when not receiving commands.  This enables good hovering when not sending commands.

``flip(direction)`` Sends the flip command to the minidrone. Valid directions to flip are: front, back, right, left.

``turn_degrees(degrees)`` Turns the minidrone in place the specified number of degrees.
The range is -180 to 180.  This can be accomplished in direct_fly() as well but this one uses the
internal minidrone sensors (which are not sent out right now) so it is more accurate.

``fly_direct(roll, pitch, yaw, vertical_movement, duration)`` Fly the minidrone directly using the
specified roll, pitch, yaw, and vertical movements.  The commands are repeated for duration seconds.
Note there are currently no sensors reported back to the user to ensure that these are working but hopefully
that is addressed in a future firmware upgrade.  Each value ranges from -100 to 100 and is essentially a percentage
and direction of the max_tilt (for roll/pitch) or max_vertical_speed (for vertical movement).

``set_max_tilt(degrees)`` Set the maximum tilt in degrees.  Be careful as this makes your drone go slower or faster!
It is important to note that the fly_direct command uses this value in conjunction with the -100 to 100 percentages.

``set_max_vertical_speed(speed)`` Set the maximum vertical speed in m/s.  Be careful as this makes your drone go up/down faster!

Pausing or sleeping in a thread safe manner
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``smart_sleep(seconds)`` This sleeps the number of seconds (which can be a floating point) but wakes for all
BLE or wifi notifications. **Note, if you are using BLE: This comamnd is VERY important**.  **NEVER** use regular
time.sleep() as your BLE will disconnect regularly! Use smart_sleep instead!  time.sleep() is ok if you are using
wifi but smart_sleep() handles that for you.

USB accessories: Claw and Gun
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
``open_claw()`` Open the claw.  Note that the claw should be attached for this to work.
The id is obtained from a prior ``ask_for_state_update()`` call.  Note that you cannot use the claw with the FPV camera attached.

``close_claw()`` Close the claw. Note that the claw should be attached for this to work.
The id is obtained from a prior ``ask_for_state_update()`` call.  Note that you cannot use the claw with the FPV camera attached.

``fire_gun()`` Fires the gun.  Note that the gun should be attached for this to work.
The id is obtained from a prior ``ask_for_state_update()`` call.  Note that you cannot use the gun with the FPV camera attached.

Swing specific commands
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
``set_plane_gear_box(state)`` Choose the swing angle in plane mode. There are 3 tilt modes: gear_1, gear_2, gear_3.
Warning gear_3 is very fast.

``set_flying_mode(mode)`` Choose flight mode between: quadricopter, plane_forward, plane_backward.

Ground facing camera
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
``take_picture()``` The minidrone will take a picture with the downward facing camera.  It only stores up to 40 pictures
internally so this function deletes them after 35 have been taken.  Make sure you are downloading them either
using the mobile interface or through the python code.

**Note**: Parrot broke the ability to access the groundcam in their latest (3.0.25) firmware upgrade.  We will reenable these
functions as soon as parrot fixes the firmware but for now, they will only work in versions 3.0.24 and below.

``get_groundcam_pictures_names()`` Returns the names of the pictures stored internally from the groundcam. Only for the mambo.

``get_groundcam_picture(name)`` Returns the picture with the specified name. Only for the mambo.

Sensor related commands
^^^^^^^^^^^^^^^^^^^^^^^

``ask_for_state_update()`` This sends a request to the minidrone to send back ALL states
(this includes the claw and gun states).  This really only needs to be called once at the start of the program
to initialize some of the state variables.  If you are on wifi, many of the other variables are sent at 2Hz. If you are
on BLE, you will want to use this command to get more state information but keep in mind it will be slow.
This command will return immediately but you should wait a few seconds before using the new state information
as it has to be updated.


Mambo sensors
-------------

All of the sensor data that is passed back to the program is saved.  Note that Parrot sends back more
information via wifi than via BLE, due to the limited BLE bandwidth.  The sensors are saved in Minidrone.sensors.
This is an instance of a MamboSensors class, which can be seen at the top of the Minidrone.py file.

The easiest way to interact with the sensors is to call:

``minidrone.set_user_sensor_callback(function, args)``. This sets a user callback function with optional
arguments that is called each time a sensor is updated.  The refresh rate on wifi is 2Hz.

The sensors are:

* battery (defaults to 100 and stays at that level until a real reading is received from the drone)
* flying_state: This is updated as frequently as the drone sends it out and can be one of "landed", "takingoff", "hovering", "flying", "landing", "emergency", "rolling", "init".  These are the values as specified in `minidrone.xml <https://github.com/amymcgovern/pyparrot/blob/master/commandsandsensors/minidrone.xml>`_.
* gun_id: defaults to 0 (as far as I can tell, it is only ever 0 when it comes from the drone anyway)
* gun_state: "READY" or "BUSY" as sent by the drone, if a gun is attached. Defaults to None.
* claw_id: defaults to 0
* claw_state: "OPENING", "OPENED", "CLOSING", "CLOSED" as sent by the drone, if a claw is attached.  Defaults to None.
* speed_x, speed_y, speed_z, speed_ts: the speed in x (forward > 0), y (right > 0), and z (down > 0).  The ts is the timestamp that the speed was valid.
* altitude, altitude_ts: wifi only, altitude in meters.  Zero is where you took off.  The ts is the timestamp where the altitude was valid.
* quaternion_w, quaternion_x, quaternion_y, quaternion_z, quaternion_ts: wifi only.  Quaternion as estimated from takeoff (which is set to 0). Ranges from -1 to 1. ts is the timestamp where this was valid.
* ``get_estimated_z_orientation()``: returns the estimated orientation using the unit quaternions.  Note that 0 is the direction the drone is facing when you boot it up
* sensors_dict: all other sensors are saved by name in a dictionary.  The names come from the `minidrone.xml <https://github.com/amymcgovern/pyparrot/blob/master/commandsandsensors/minidrone.xml>`_ and `common.xml <https://github.com/amymcgovern/pyparrot/blob/master/commandsandsensors/common.xml>`_.
