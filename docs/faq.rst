.. title:: Frequently Asked Questions

.. faq:

Frequently Asked Questions
====================================

Below is a list of common errors and how to fix them.

Vision isn't showing anything on the minidrone
----------------------------------------------

The Minidrone camera puts itself into a "resting" state after not flying for several minutes.  To solve this, you
either need to fly again (a simple takeoff and landing will suffice) or reboot the minidrone and reconnect.

I'm using windows and my drone gives me lots of timeout errors
---------------------------------------------------------------
This is a windows security setting and it can be fixed.  Go into your windows firewall settings (control panel,
system and security, allow a program through Windows Firewall) and change the settings
for python.exe to be allowed through the firewall for both home/private networks and public networks. Your sensors will
suddenly be able to send data to your machine and safe_land will start working again as well as any sensors!

My drone does takeoff and landing but nothing else
--------------------------------------------------

Likely you have the remote controller on and attached!  For some reason, if the remote is on,
it will allow the python code to takeoff & land but no other commands will work.
Turn off the remote and your code should work fine!

Errors connecting to the drone
------------------------------

There are two common errors that I see when flying.  One requires the drone to reboot and one requires the
computer controlling the drone to reboot.

Connection failed
^^^^^^^^^^^^^^^^^
If you fail to connect to the drone, you will see an error message like this:

::

    connection failed: did you remember to connect your machine to the Drone's wifi network?

The most likely cause is that you forgot to connect to the drone's wifi.  If you tried to connect,
sometimes that connection fails.  Try again or let the connection sit for a minute and try your program again.

If you are on the wifi but you get connection refused errors, reboot the drone.

Address in use
^^^^^^^^^^^^^^

The second common error is about the address being in use, as shown below.

::

    OSError: [Errno 48] Address already in use


There are two ways to fix this, depending on the issue.  It is possible you tried to run a second program while
you still had a first program running.  If this is the case, make sure you stop all of your minidrone programs and then
restart only one.  If you are not running a second minidrone program, then the solution is to reboot.  This sometimes
happens due to the program crashing before it releases the socket.
