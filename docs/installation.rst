.. title:: Installation

.. installation:

Installation
===============

You have two choices for installing pyparrot: using the ``source`` code directly or downloading with ``pip``.
**Note** Pyparrot will only work with python 3.  This choice was made because the support for multi-threaded
programs is improved in python 3.

Requirements
------------

The choice of related packages is dependent on your choice of drone (Mambo, Mambo FPV, Bebop 1 or 2, Swing, Anafi) and
to the operating system that you will be using to develop.

Hardware/Drone requirements
^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Parrot Mambo FPV**: If you have a Mambo FPV (e.g. you have the camera), you can use the wifi interface.  The wifi interface will work on Mac, Linux, or Windows.

* **Parrot Mambo Fly or Code**: If you have a Mambo without the camera, you will use the BLE interface. pyparrot currently only supports Linux for BLE.  The BLE interface was developed on a Raspberry Pi 3 Model B but it has been tested on other Linux machines.

* **Parrot Swing**: To use the Swing you will use the BLE interface.

* **Parrot Bebop 2**: The Bebop interface was tested on a Bebop 2 using a laptop with wifi (any wifi enabled device should work).

* **Parrot Bebop 1**: A Bebop 1 will also work with any wifi enabled device.

* **Parrot Anafi**: Per the development board, the Anafi should work with very minor changes.  I will work to officially suppport it once the SDK from parrot is released for it.

Software requirements
^^^^^^^^^^^^^^^^^^^^^

Software requirements are listed below by type of connection to the drone.

* All drones:  Python 3

   I use the `<https://www.anaconda.com/download/>`_:: installer and package manager for python.  Note, when you
install anaconda, install the Visual Studio option, especially if you have windows.  Otherwise you will need to install
Visual Studio separately.  The zeroconf package (listed below) requires developer tools because it needs to be compiled.

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


* BLE connection: pybluez (note this is ONLY for support without the camera!) This is ONLY supported on linux.
To install the BLE software do the following:

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

Installation guide for windows users who might need more help
-------------------------------------------------------------

Thank you to @JackdQuinn for contributing this.

Make sure you install **Visual Studio** either using Anaconda or by downloading it from Microsoft.  Note that Visual
Studio is free but it is required for compilation of the wifi module zeroconf, and specifically of the netifaces
module that zeroconf requires.  It is a very large download if you chose to do it outside of anaconda so you will
want to start that download first.

If you install python without anaconda, when you install choose Special install Python and
click add python to path (this will clear up some command line call issues).

Again, if you chose regular python and not anaconda, you can check installation by typing py in the windows command line.

::

    py

Once you are sure that python started, you will want to quit python.  type: ``quit()`` to exit python

::

    quit()

If you chose to use anaconda, bring up the anaconda menu and open an anaconda prompt to verify that it installed.
The rest of the instructions depend on whether you chose python or anaconda for your installation.  If you chose python,
use the windows command prompt for pip.  If you chose anaconda, use your anaconda prompt.

If you type the pip command (with no options), it will produce a long list of options.  This tells you that you
are at the right command prompt to do the rest of the installation.
**Note, the pip command will not work inside of python.**  This is a command prompt command, not a python command.

::

    pip


Sometimes pip tells you that it wants to upgrade.  For windows, the command is:

::

    python -m pip install -U pip

To actually install, use the commands described above (and repeated here).

::

    pip install untangle
    pip install pyparrot
    pip install zeroconf

**Note that visual studio is a requirement for zeroconf**

Testing your install
^^^^^^^^^^^^^^^^^^^^

The first step is to connect your connect your controlling device (laptop, computer, etc) to the wifi for the drone.
Look for a wifi network named Mambo_number where number changes for each drone.

After connection to your drone its time to run code!  You can download all the example code from
these docs.  Below is a short set of commands of how to run that code.

Run code by cd'ing down to the directory (the folder your python code is in) and running the desired python file from the cmd line

Example:
    * open command line either through windows or anaconda (depending on your installation method)
    * type: ``cd desktop``
    * this will Change your Directory to the desktop
    * type: ``dir``
    * this will display a list of all the folders (directories) on the desktop
    * type: ``cd yourFolderNameHere``
    * type: ``dir``
    * this will display all the files and folders in the directory
    * type: ``py TheNameOfTheFileYouWantToRun.py`` or ``python TheNameOfTheFileYouWantToRun.py``
    * When you click enter the file will begin to run, if you are using the demo scripts you should see lots of nice feedback as it changes states.  You can use the arrow keys to go through your history of commands which can save you lots of time if your file names are long.
    * If you have several connects and disconnects try restarting your computer or resetting your ip (for the more technically inclined)
    * If you have crashes where the drone is flipping to one side when it shouldn't check the blades and bumpers. The bumpers can shift after a crash and prevent the blades from spinning, or slow down their spin, which causes unintended flips