import pygame
import sys
from pyparrot.Minidrone import Swing

def joystick_init():
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


def mapping_button(joystick, drone_commands):
    mapping = {}

    for command in drone_commands:
        print("Press the key", command)
        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button not in (value for value in mapping.values()):
                        mapping[command] = event.button
                        done = True

    return mapping


def mapping_axis(joystick, axes):
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


def parse_button(drone_commands, button):
    commands = drone_commands[button][0]
    args = drone_commands[button][-1]

    len_commands = len(commands)
    len_args = len(args)

    command = commands[0]
    arg = args[0]
    if len_commands == 1:
        if len_args == 1:
            command(arg)

        else:
            command(arg)

            _args = args[1:]
            drone_commands[button][-1] = _args+[arg]

    else:
        if len_args == 1:
            command(arg)

            _commands = commands[1:]
            drone_commands[button][0] = _commands+[command]
        else:
            command(arg)

            _commands = commands[1:]
            drone_commands[button][0] = _commands+[command]

            _args = args[1:]
            drone_commands[button][-1] = _arg+[arg]


def main_loop(joystick, drone_commands, mapping_button, mapping_axis):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                pass
            if event.type == pygame.JOYBUTTONUP:
                pass

        pitch = round((joystick.get_axis(mapping_axis["pitch"])+0.0001)*-100,0)
        roll = round((joystick.get_axis(mapping_axis["roll"])+0.0001)*100,0)
        yaw = round((joystick.get_axis(mapping_axis["yaw"])+0.0001)*100,0)
        vertical = round((joystick.get_axis(mapping_axis["vertical"])+0.0001)*-100,0)

        swing.fly_direct(roll, pitch, yaw, vertical, 0.1)

        for button, value in mapping_button.items():
            if joystick.get_button(value):
                parse_button(drone_commands, button)



if __name__ == "__main__":
    swing = Swing("e0:14:04:a7:3d:cb")

    drone_commands = {
                        "takeoff_landing":[
                                            [swing.safe_takeoff, swing.safe_land],
                                            [5]
                                           ],
                        "fly_mode":[
                                    [swing.set_flying_mode],
                                    ["quadricopter", "plane_forward"]
                                   ],
                        "plane_gear_box_up":[
                                             [swing.set_plane_gear_box],
                                             [((swing.sensors.plane_gear_box[:-1]+str(int(swing.sensors.plane_gear_box[-1])+1)) if swing.sensors.plane_gear_box[-1] != "3" else "gear_3")]
                                            ],
                        "plane_gear_box_down":[
                                               [swing.set_plane_gear_box],
                                               [((swing.sensors.plane_gear_box[:-1]+str(int(swing.sensors.plane_gear_box[-1])-1)) if swing.sensors.plane_gear_box[-1] != "1" else "gear_1")]
                                            ]
                    }

    axes = ["pitch", "roll", "yaw", "vertical"]

    joystick = joystick_init()

    mapping_button = mapping_button(joystick, drone_commands)
    mapping_axis = mapping_axis(joystick, axes)

    swing.connect(10)
    swing.flat_trim()

    main_loop(joystick, drone_commands, mapping_button, mapping_axis)
