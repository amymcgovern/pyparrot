"""
GUI for AI class using drones.  Allows you to quickly create a map of
a room with obstacles for navigation and search.

Amy McGovern dramymcgovern@gmail.com
"""

from tkinter import *
import numpy as np
from tkinter import filedialog
import os
import pickle

class DroneGUI:
    def __init__(self):
        self.root = Tk()
        self.room_map = None

    def translate_click(self, event):
        print("clicked at", event.x, event.y)
        center_x = event.x
        center_y = event.y

        # calculate the lower left corner of the box
        factor = 10 * self.scale_val
        lower_x = int(center_x / factor) * factor
        lower_y = int(center_y / factor) * factor
        print("lower x and y are ", lower_x, lower_y)

        return (center_x, center_y, lower_x, lower_y)

    def draw_obstacle_click(self, event):
        """
        Draw a gray box for an obstacle at button 1 clicks

        :param event:
        :return:
        """
        (center_x, center_y, lower_x, lower_y) = self.translate_click(event)
        factor = 10 * self.scale_val

        self.draw_obstacle(lower_x,lower_y, factor, color="#7575a3")

        # and save the click into the map
        map_x = int(center_x / factor)
        map_y = self.room_map.shape[1] - int(center_y / factor) - 1
        print("map x and y are ", map_x, map_y)
        self.room_map[map_x, map_y] = 1

    def draw_goal_click(self, event):
        """
        Draw a green box for a goal at button 1 clicks

        :param event:
        :return:
        """
        (center_x, center_y, lower_x, lower_y) = self.translate_click(event)
        factor = 10 * self.scale_val

        self.draw_obstacle(lower_x,lower_y, factor, color="green")

        # and save the click into the map
        map_x = int(center_x / factor)
        map_y = self.room_map.shape[1] - int(center_y / factor) - 1
        print("map x and y are ", map_x, map_y)
        self.room_map[map_x, map_y] = 3

    def draw_start_click(self, event):
        """
        Draw a red box for the start

        :param event:
        :return:
        """
        (center_x, center_y, lower_x, lower_y) = self.translate_click(event)
        factor = 10 * self.scale_val

        self.draw_obstacle(lower_x,lower_y, factor, color="red")

        # and save the click into the map
        map_x = int(center_x / factor)
        map_y = self.room_map.shape[1] - int(center_y / factor) - 1
        print("map x and y are ", map_x, map_y)
        self.room_map[map_x, map_y] = 2

    def draw_obstacle(self, x, y, size, color):
        # draw the rectangle
        self.room_draw.create_rectangle(x, y, x + size, y + size, fill=color)

    def set_scale(self):
        try:
            self.scale_val = int(self.scale.get())
        except:
            self.scale_val = 1

    def create_room(self):
        """
        Create the window with the room grid

        Uses the scale parameter set from the first gui window to decide how big the boxes are (scale must be an int)

        Draws a grid with black lines every 10 * scale pixels (e.g. every decimeter) and then draws a thicker
        line every meter (e.g. every 10 lines)

        :return:
        """
        length = float(self.length.get())
        height = float(self.height.get())

        # initialize the internal map
        self.room_map = np.zeros((int(length * 10), int(height * 10)))
        print(self.room_map.shape)

        print("Length is %0.1f and height is %0.1f" % (length, height))

        self.set_scale()
        self.draw_room(length, height)

    def draw_room(self, length, height):
        # each pixel is scale * 1 cm so multiply by 100 to get the width/height from the meters
        canvas_width = int(length * 100 * self.scale_val)
        canvas_height = int(height * 100 * self.scale_val)

        # create the blank canvas
        room = Toplevel(self.root)

        # put the menu into the room
        # menu code mostly from
        # https://www.python-course.eu/tkinter_menus.php
        menu = Menu(room)
        room.config(menu=menu)
        filemenu = Menu(menu)
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Save Map", command=self.save_file_menu)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)

        helpmenu = Menu(menu)
        menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About...", command=self.about_menu)

        # draw the room
        self.room_draw = Canvas(room, width=canvas_width, height=canvas_height, bg="#ffffe6")
        self.room_draw.pack()

        # how to draw a checkered canvas from
        # https://www.python-course.eu/tkinter_canvas.php
        # vertical lines at an interval of "line_distance" pixel
        line_distance = 10 * self.scale_val
        for x in range(line_distance, canvas_width, line_distance):
            if (x % (line_distance * 10) == 0):
                self.room_draw.create_line(x, 0, x, canvas_height, fill="red", width=2)
            else:
                self.room_draw.create_line(x, 0, x, canvas_height, fill="black")

        # horizontal lines at an interval of "line_distance" pixel
        for y in range(line_distance, canvas_height, line_distance):
            if (y % (line_distance * 10) == 0):
                self.room_draw.create_line(0, y, canvas_width, y, fill="red", width=2)
            else:
                self.room_draw.create_line(0, y, canvas_width, y, fill="black")

        # bind the button clicks to draw out the map
        self.room_draw.bind("<Button-1>", self.draw_obstacle_click)
        self.room_draw.bind("<Button-2>", self.draw_start_click)
        self.room_draw.bind("<Button-3>", self.draw_goal_click)

        # add in the obstacles (if any exist already)
        (xs, ys) = np.nonzero(self.room_map)
        factor = 10 * self.scale_val
        for i, x in enumerate(xs):
            y = ys[i]
            lower_x = x * factor
            lower_y = (self.room_map.shape[1] - y - 1) * factor
            if (self.room_map[x, y] == 1):
                self.draw_obstacle(lower_x, lower_y, factor, color="#7575a3")
            elif (self.room_map[x, y] == 2):
                self.draw_obstacle(lower_x, lower_y, factor, color="red")
            elif (self.room_map[x, y] == 3):
                self.draw_obstacle(lower_x, lower_y, factor, color="green")

    def draw_map_from_file(self):
        width = self.room_map.shape[1] / 10.0
        length = self.room_map.shape[0] /10.0
        print("length and width of loaded room are ", length,width)
        print("Scale is "), self.scale_val
        self.draw_room(length, width)

    def open_file_menu(self):
        """
        Load a map from a file
        :return:
        """
        filename = filedialog.askopenfilename(initialdir=os.getcwd(),
                                              title="Select map file",
                                              filetypes=(("map files", "*.map"), ("all files", "*.*")))

        fp = open(filename, "rb")
        self.scale_val = pickle.load(fp)
        self.room_map = pickle.load(fp)
        #print("scale val is ", self.scale_val)
        #print("room map is ", self.room_map)
        fp.close()
        self.draw_map_from_file()

    def save_file_menu(self):
        """
        Bring up a save file dialog and then save
        :return:
        """
        filename = filedialog.asksaveasfile(initialdir=os.getcwd(),
                                            title="Save map file",
                                            defaultextension=".map")
        print("saving to ", filename.name)
        fp = open(filename.name, "wb")
        pickle.dump(self.scale_val, fp)
        pickle.dump(self.room_map, fp)
        fp.close()


    def about_menu(self):
        pass

    def draw_initial_gui(self):
        """
        Draws the intial GUI that lets you make a new room
        or load one from a file
        :return:
        """

        # menu code mostly from
        # https://www.python-course.eu/tkinter_menus.php
        menu = Menu(self.root)
        self.root.config(menu=menu)
        filemenu = Menu(menu)
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Open Map", command=self.open_file_menu)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)

        helpmenu = Menu(menu)
        menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About...", command=self.about_menu)

        # draw the request to create a new room
        Label(self.root, text="Enter the size of the room you are flying in (decimals to tenths)").grid(row=0, columnspan=2)
        Label(self.root, text="Length (x) (meters)").grid(row=1)
        Label(self.root, text="Height (y) (meters)").grid(row=2)
        Label(self.root, text="1 pixel = ____ cm").grid(row=3)

        # the entry boxes
        self.length = Entry(self.root)
        self.length.grid(row=1, column=1)

        self.height = Entry(self.root)
        self.height.grid(row=2, column=1)

        self.scale = Entry(self.root)
        self.scale.grid(row=3, column=1)

        # action buttons
        Button(self.root, text='Quit', command=self.root.quit).grid(row=4, column=0, pady=4)
        Button(self.root, text='Create room', command=self.create_room).grid(row=4, column=1, pady=4)

    def go(self):
        """
        Start the main GUI loop
        :return:
        """
        mainloop()




if __name__ == "__main__":
    gui = DroneGUI()
    gui.draw_initial_gui()
    gui.go()
