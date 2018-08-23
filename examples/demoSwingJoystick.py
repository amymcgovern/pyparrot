import pygame
import sys
from pyparrot.Minidrone import Swing

def joystick_init():
    """
    Initializes the controller, allows the choice of the controller.
    If no controller is detected returns an error.

    :param:
    :return joystick:
    """
    pygame.init()
    pygame.joystick.init()

    joystick_count = pygame.joystick.get_count()

    if joystick_count > 0:
        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()

            name = joystick.get_name()
            print([i], name)

            joystick.quit()

    else:
        sys.exit("Error: No joystick detected")

    selected_joystick = eval(input("Enter your joystick number:"))

    if selected_joystick not in range(joystick_count):
        sys.exit("Error: Your choice is not valid")

    joystick = pygame.joystick.Joystick(selected_joystick)
    joystick.init()

    return joystick


def mapping_button(joystick, dict_commands):
    """
    Associating a controller key with a command in dict_commands.

    :param joystick, dict_commands:
    :return mapping:
    """
    mapping = {}

    for command in dict_commands:
        print("Press the key", command)
        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button not in (value for value in mapping.values()):
                        mapping[command] = event.button
                        done = True

    return mapping


def mapping_axis(joystick, axes=["pitch", "roll", "yaw", "vertical"]):
    """
    Associating the analog thumbsticks of the controller with a command in dict commands

    :param joystick, dict_commands:
    :return mapping:
    """
    mapping = {}

    for i in axes:
        print("Push the", i, "axis")
        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    if event.axis not in (value for value in mapping.values()):
                        mapping[i] = event.axis
                        done = True

    return mapping


def _parse_button(dict_commands, button):
    """
    Send the commands to the drone.
    If multiple commands are assigned to a key each command will be sent one by one to each press.

    :param dict_commands, button:
    :return:
    """
    commands = dict_commands[button][0]
    args = dict_commands[button][-1]

    command = commands[0]
    arg = args[0]

    if len(commands) == 1:
        if len(args) == 1:
            command(arg)

        else:
            command(arg)
            dict_commands[button][-1] = args[1:]+[arg]

    else:
        if len(commands) == 1:
            command(arg)
            dict_commands[button][0] = commands[1:]+[command]

        else:
            command(arg)
            dict_commands[button][0] = commands[1:]+[command]
            dict_commands[button][-1] = args[1:]+[arg]


def main_loop(joystick, dict_commands, mapping_button, mapping_axis):
    """
    First connects to the drone and makes a flat trim.
    Then in a loop read the events of the controller to send commands to the drone.

    :param joystick, dict_commands, mapping_button, mapping_axis:
    :return:
    """
    swing.connect(10)
    swing.flat_trim()

    while True:
        pygame.event.get()

        pitch = joystick.get_axis(mapping_axis["pitch"])*-100
        roll = joystick.get_axis(mapping_axis["roll"])*100
        yaw = joystick.get_axis(mapping_axis["yaw"])*100
        vertical = joystick.get_axis(mapping_axis["vertical"])*-100

        swing.fly_direct(roll, pitch, yaw, vertical, 0.1)

        for button, value in mapping_button.items():
            if joystick.get_button(value):
                _parse_button(dict_commands, button)


if __name__ == "__main__":
    swing = Swing("e0:14:04:a7:3d:cb")

    #Example of dict_commands
    dict_commands = {
                        "takeoff_landing":[ #Name of the button
                                            [swing.safe_takeoff, swing.safe_land],#Commands execute one by one
                                            [5]#Argument for executing the function
                                           ],
                        "fly_mode":[
                                    [swing.set_flying_mode],
                                    ["quadricopter", "plane_forward"]
                                   ],
                        "plane_gear_box_up":[
                                             [swing.set_plane_gear_box],
                                             [((swing.sensors.plane_gear_box[:-1]+str(int(swing.sensors.plane_gear_box[-1])+1)) if swing.sensors.plane_gear_box[-1] != "3" else "gear_3")]#"gear_1" => "gear_2" => "gear_3"
                                            ],
                        "plane_gear_box_down":[
                                               [swing.set_plane_gear_box],
                                               [((swing.sensors.plane_gear_box[:-1]+str(int(swing.sensors.plane_gear_box[-1])-1)) if swing.sensors.plane_gear_box[-1] != "1" else "gear_1")]#"gear_3" => "gear_2" => "gear_1"
                                            ]
                    }

    joystick = joystick_init()

    mapping_button = mapping_button(joystick, dict_commands)
    mapping_axis = mapping_axis(joystick)

    main_loop(joystick, dict_commands, mapping_button, mapping_axis)
