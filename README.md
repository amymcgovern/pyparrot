# pyparrot
Python interface for Parrot Drones

This is a redesign of my [pymambo](https://github.com/amymcgovern/pymambo) repository.  It is more general and handles both the wifi and BLE interfaces for the mambvo and also handles flying other parrot drones (tested on the Bebop 2).  

This interface was developed to teach kids (K-12) STEM concepts (programming, math, and more) by having them program a drone to fly autonomously.  Anyone can use it who is interested in autonomous drone programming!  

## Requirements

### Hardware

* Parrot Mambo: If you use the wifi interface, it requires a Mambo FPV (e.g. you need the camera).  If you want to use the BLE interface, it will work on older Mambos (without the FPV camera) but it will require a linux machine with BLE support.  The BLE interface was developed and tested on a Raspberry Pi 3 Model B.  It should work on any linux machine with BLE support.

* Parrot Bebop 2: The Bebop interface was tested on a Bebop 2 using a laptop with wifi (any wifi enabled device should work).

### Software

Software requirements are listed below by type of connection to the drone.

* All drones:  Python 3 and untangle package

   I use the [anaconda](https://www.anaconda.com/download/) installer and package manager for python. 

* Wifi connection: [zeroconf](https://pypi.python.org/pypi/zeroconf)

   To install zeroconf software do the following:

   ```
   pip install zeroconf
   ```

* BLE connection: pybluez

   To install the BLE software do the following:

   ```
   sudo apt-get install bluetooth
   sudo apt-get install bluez
   sudo apt-get install python-bluez
   pip install untangle
   ```

   It is possible you need to install bluepy (if it isn't already there).  These commands should do it:
   ```
   sudo apt-get install python-pip libglib2.0-dev
   sudo pip install bluepysudo apt-get update
   ```

To install the pyparrot code, download or clone the repository.

## Using the pyparrot library

If you want to use wifi for either the Mambo or the Bebop, you need to connect your controling device (laptop, computer, etc) to the wifi for the drone.  If you want to use BLE, you will first need to find the BLE address of your Mambo.  BLE permissions on linux require that this command run in sudo mode.  To this this, from the directory where you installed the pyparrot code, type:

```
sudo python findMambo.py
```

This will identify all BLE devices within hearing of the Pi.  The Mambo will be identified at the end.  Save the address and use it in your connection code (discussed below).  If findMambo does not report "FOUND A MAMBO!", then be sure your Mambo is turned on when you run the findMambo code and that your Pi (or other linux box) has its BLE interface turned on.

## Quick start:  Demos

I have provided a set of [example](https://github.com/amymcgovern/pyparrot/tree/master/examples) scripts for both the Mambo and the Bebop.  Note that you will need to edit the mambo scripts to either use your own BLE address or to ensure that use_wifi=True is set, so that it connects using wifi.  Note that you do not need to run any of the other code in sudo mode!  That was only for discovery.

I have provided four demo programs for the Mambo and two for the Bebop. 

* **Mambo**
   * [demoMamboTricks.py](https://github.com/amymcgovern/pyparrot/blob/master/examples/demoMamboTricks.py) 

      ```
      python examples/demoMamboTricks.py
      ```
      demoMamboTricks.py will take off, demonstrate all 4 types of flips, and then land.
      
   * [demoMamboDirectFlight.py](https://github.com/amymcgovern/pyparrot/blob/master/examples/demoMamboDirectFlight.py)

      ```
      python examples/demoMamboDirectFlight.py
      ```
      demoMamboDirectFlight.py will demonstrate directly controlling the roll, pitch, yaw, and vertical control.  Make sure you try this one in a large enough room!
      
   * [demoMamboClaw.py](https://github.com/amymcgovern/pyparrot/blob/master/examples/demoMamboClaw.py)

      ```
      python examples/demoMamboClaw.py
      ```
      demoMamboClaw shows you how to control the claw.  In this demo program, the mambo takes off, opens and closes the claw, and lands again.  
      
   * [demoMamboGun.py](https://github.com/amymcgovern/pyparrot/blob/master/examples/demoMamboGun.py)
   
      ```
      python examples/demoMamboGun.py
      ```
      demoMamboGun shows you how to control the gun.  In this demo program, the mambo takes off, fires the gun, and lands again.
   
* **Bebop**
   * [demoBebopTricks.py](https://github.com/amymcgovern/pyparrot/blob/master/examples/demoBebopTricks.py)
      ```
      python examples/demoBebopTricks.py
      ```

      The bebop can flip just like the Mambo!  This does the exact same thing as the Mambo tricks demo: take off, flip in all 4 directions, land
   
   * [demoBebopDirectFlight.py](https://github.com/amymcgovern/pyparrot/blob/master/examples/demoBebopDirectFlight.py)

      ```
      python examples/demoBebopDirectFlight.py
      ```

      The bebop can also be directly controlled for roll, pitch, yaw, and vertical.  This program demonstrates the use of all 4 of  these directions.  Be sure to run this in a large enough space!

## Mambo commands

Each of the commands available to control the mambo is listed below with its documentation.  The code is also well documented.  All of the functions preceeded with an underscore are intended to be internal functions are not listed below.

* ```Mambo(address, use_wifi=True/False)``` create a mambo object with the specific harware address (found using findMambo).  The use_wifi argument defaults to False (which means BLE is the default).  Set to True to use wifi.  You can only use wifi if you have a FPV camera installed on your Mambo!
* ```connect(num_retries)``` connect to the Mambo either using BLE services and characteristics or wifi (specified when you created the Mambo object).  This can take several seconds to ensure the connection is working.  You can specify a maximum number of re-tries.  Returns true if the connection suceeded or False otherwise.  
* ```disconnect``` disconnect from the BLE connection
* ```takeoff()``` Sends a single takeoff command to the mambo.  This is not the recommended method.
* ```safe_takeoff(timeout)``` This is the recommended method for takeoff.  It sends a command and then checks the sensors (via flying state) to ensure the mambo is actually taking off.  Then it waits until the mambo is flying or hovering to return.  It will timeout and return if the time exceeds timeout seconds.
* ```land()``` Sends a single land command to the mambo.  This is not the recommended method.
* ```safe_land(timeout)``` This is the recommended method to land the mambo.  Sends commands until the mambo has actually reached the landed state. It will timeout and return if the time exceeds timeout seconds.
* ```hover()``` Puts the mambo into hover mode.  This is the default mode if it is not receiving commands.
* ```flip(direction)``` Sends the flip command to the mambo. Valid directions to flip are: front, back, right, left.
* ```turn_degrees()``` Turns the mambo in place the specified number of degrees.  The range is -180 to 180.  This can be accomplished in direct_fly() as well but this one uses the internal mambo sensors (which are not sent out right now) so it is more accurate.
* ```smart_sleep()``` This sleeps the number of seconds but wakes for all BLE or wifi notifications.  This comamnd is VERY important.  **NEVER** use regular time.sleep() as your BLE will disconnect regularly!  Use smart_sleep instead!
* ```turn_on_auto_takeoff()``` This puts the mambo in throw mode.  When it is in throw mode, the eyes will blink.
* ```take_picture()``` The mambo will take a picture with the downward facing camera.  It is stored internally on the mambo and you can download them using a mobile interface.  As soon as I figure out the protocol for downloading the photos, I will add it to the python interface.
* ```ask_for_state_update()``` This sends a request to the mambo to send back ALL states (this includes the claw and gun states).  Only the battery and flying state are currently sent automatically.  This command will return immediately but you should wait a few seconds before using the new state information as it has to be updated by BLE characteristic handlers and it sends each type of state in a separate BLE/wifi packet.
* ```fly_direct(roll, pitch, yaw, vertical_movement, duration)``` Fly the mambo directly using the specified roll, pitch, yaw, and vertical movements.  The commands are repeated for duration seconds.  Note there are currently no sensors reported back to the user to ensure that these are working but hopefully that is addressed in a future firmware upgrade.  Each value ranges from -100 to 100.  
* ```open_claw()``` Open the claw.  Note that the claw should be attached for this to work.  The id is obtained from a prior ```ask_for_state_update()``` call.  Note that you cannot use the claw with the FPV camera attached.
* ```close_claw()``` Close the claw. Note that the claw should be attached for this to work.  The id is obtained from a prior ```ask_for_state_update()``` call.  Note that you cannot use the claw with the FPV camera attached.
* ```fire_gun()``` Fires the gun.  Note that the gun should be attached for this to work.  The id is obtained from a prior ```ask_for_state_update()``` call.  Note that you cannot use the claw with the FPV camera attached.

## Bebop commands

Each of the commands available to control the Bebop is listed below with its documentation.  The code is also well documented.  All of the functions preceeded with an underscore are intended to be internal functions are not listed below.  The bebop is still under very active development and is released to share but will continue to be updated.

* ```Bebop(address)``` create a mambo object with the specific harware address (found using findMambo)
* ```connect(num_retries,debug_lebel)``` connect to the Mambo's BLE services and characteristics.  This can take several seconds to ensure the connection is working.  You can specify a maximum number of re-tries.  Returns true if the connection suceeded or False otherwise.  The debug_level can be used to control the amount of printouts from the Mambo.  Set to None (default) for no printouts and 0 for all, 10 for errors only.
* ```disconnect``` disconnect from the BLE connection
* ```takeoff()``` Sends a single takeoff command to the mambo.  This is not the recommended method.
* ```safe_takeoff()``` This is the recommended method for takeoff.  It sends a command and then checks the sensors (via flying state) to ensure the mambo is actually taking off.  Then it waits until the mambo is flying or hovering to return.
* ```land()``` Sends a single land command to the mambo.  This is not the recommended method.
* ```safe_land()``` This is the recommended method to land the mambo.  Sends commands until the mambo has actually reached the landed state.
* ```hover()``` Puts the mambo into hover mode.  This is the default mode if it is not receiving commands.
* ```flip(direction)``` Sends the flip command to the mambo. Valid directions to flip are: front, back, right, left.
* ```turn_degrees()``` Turns the mambo in place the specified number of degrees.  The range is -180 to 180.  This can be accomplished in direct_fly() as well but this one uses the internal mambo sensors (which are not sent out right now) so it is more accurate.
* ```smart_sleep()``` This sleeps the number of seconds but wakes for all BLE notifications.  This comamnd is VERY important.  NEVER use regular time.sleep() as your BLE will disconnect regularly!  Use smart_sleep instead!
* ```turn_on_auto_takeoff()``` This puts the mambo in throw mode.  When it is in throw mode, the eyes will blink.
* ```take_picture()``` The mambo will take a picture with the downward facing camera.  It is stored internally on the mambo and you can download them using a mobile interface.  As soon as I figure out the protocol for downloading the photos, I will add it to the python interface.
* ```ask_for_state_update()``` This sends a request to the mambo to send back ALL states (this includes the claw and gun states).  Only the battery and flying state are currently sent automatically.  This command will return immediately but you should wait a few seconds before using the new state information as it has to be updated by BLE characteristic handlers and it sends each type of state in a separate BLE packet.
* ```fly_direct(roll, pitch, yaw, vertical_movement, duration)``` Fly the mambo directly using the specified roll, pitch, yaw, and vertical movements.  The commands are repeated for duration seconds.  Note there are currently no sensors reported back to the user to ensure that these are working but hopefully that is addressed in a future firmware upgrade.  Each value ranges from -100 to 100.  
* ```open_claw()``` Open the claw.  Note that the claw should be attached for this to work.  The id is obtained from a prior ```ask_for_state_update()``` call.
* ```close_claw()``` Close the claw. Note that the claw should be attached for this to work.  The id is obtained from a prior ```ask_for_state_update()``` call.
* ```fire_gun()``` Fires the gun.  Note that the gun should be attached for this to work.  The id is obtained from a prior ```ask_for_state_update()``` call.


## Planned updates/extensions

This is a work in progress.  Planned extensions include:

* FPV camera.  Update: the FPV camera works but the Raspberry Pi can't handle the framerate so the devleopment is only initial. 
* Downloading pictures from the downward facing camera.  We can take photos from it (mambo.take_picture()) but I haven't figured out the protocol to download the photos remotely yet.  When I figure that out, I will update the code.
* Sensors.  The mambo currently only sends a limited number of sensors back regularly (flying state and battery).  They have stated they will improve this in a future firmware release.  I will update the code to handle the new sensors (hopefully including altitude!) when the firmware is updated.  11/2: working on the wifi sensor data.

## Major updates:
* 10/6/2017: General BLE stability improvements with the specific goal of flying multiple mambos at once.  Now if BLE disconnects, it catches that event and re-connects.  
* 10/6/2017: Multi-mambo flight is now possible so long as you control each one in a separate python file (this seems to be a limitation within bluepy). 
* 11/3/2017: Added MamboVision code that correctly connects and grabs images from the FPV camera but the Raspberry Pi can't handle the 30 FPS so the code is not finished.  Also updated the states that are parsed via BLE.
