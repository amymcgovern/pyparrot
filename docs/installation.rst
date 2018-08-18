.. title:: Installation

.. installation:

Installation
===============

You have two choices for installing pyparrot: using the ``source`` code directly or downloading with ``pip``.
**Note** Pyparrot will only work with python 3.  This choice was made because the support for multi-threaded
programs is improved in python 3.

Requirements
------------

The choice of related packages is dependent on your choice of drone (Mambo, Mambo FPV, Beebop 2, Swing) and
to the operating system that you will be using to develop.

Hardware/Drone requirements
^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Parrot Mambo FPV**: If you have a Mambo FPV (e.g. you have the camera), you can use the wifi interface.  The wifi interface will work on Mac, Linux, or Windows.

* **Parrot Mambo Fly or Code**: If you have a Mambo without the camera, you will use the BLE interface. pyparrot currently only supports Linux for BLE.  The BLE interface was developed on a Raspberry Pi 3 Model B but it has been tested on other Linux machines.

* **Parrot Swing**: To use the Swing you will use the BLE interface.

* **Parrot Bebop 2**: The Bebop interface was tested on a Bebop 2 using a laptop with wifi (any wifi enabled device should work).

* **Parrot Bebop**: A Bebop one will also work with any wifi enabled device.


Software requirements
^^^^^^^^^^^^^^^^^^^^^

Software requirements are listed below by type of connection to the drone.

* All drones:  Python 3

   I use the `<https://www.anaconda.com/download/>`_:: installer and package manager for python.

* All drones: untangle package (this is used to parse the xml files in the parrot SDK)


::

  pip install untangle



* Vision:  If you intend to process the camera files, you will need to install opencv and then either ffmpeg
or VLC.  I installed ffmpeg using brew for the mac but apt-get on linux should also work.  For VLC, you MUST install
the actual `VLC <https://www.videolan.org/vlc/index.html`_ program (and not just the library in python)
and it needs to be version 3.0.1 or greater.

* Wifi connection: `zeroconf <https://pypi.python.org/pypi/zeroconf>`_ To install zeroconf software do the following:

::

  pip install zeroconf


* BLE connection: pybluez (note this is ONLY for support without the camera!) To install the BLE software do the following:

::

   sudo apt-get install bluetooth
   sudo apt-get install bluez
   sudo apt-get install python-bluez


Note it is also possible that you will need to install bluepy (if it isn't already there).  These commands should do it:

::

   sudo apt-get install python-pip libglib2.0-dev
   sudo pip install bluepy
   sudo apt-get update



Installing From Source
----------------------

First download pyparrot by cloning the repository from `<https://github.com/amymcgovern/pyparrot>`_ The instructions for this are below.


::

    git clone https://github.com/amymcgovern/pyparrot
    cd pyparrot


Make sure you install the necessary other packages (wifi or BLE, vision, etc) as specified above.

Installing From Pip
-------------------

To install from pip, type


::

    pip install pyparrot


Make sure you install the necessary other packages (wifi or BLE, vision, etc) as specified above.
