import untangle
import os
from os.path import join

class DroneCommandParser:
    def __init__(self):
        # store the commandsandsensors as they are called so you don't have to parse each time
        self.command_tuple_cache = dict()

        # parse the command files from XML (so we don't have to store ids and can use names
        # for readability and portability!)

        # grab module path per http://www.karoltomala.com/blog/?p=622
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)

        self.common_commands = untangle.parse(join(dir_path, 'common.xml'))
        self.minidrone_commands = untangle.parse(join(dir_path, 'minidrone.xml'))
        self.ardrone3_commands = untangle.parse(join(dir_path, 'ardrone3.xml'))


    def get_command_tuple(self, project, myclass, cmd):
        """
        Parses the command XML for the specified class name and command name

        :param myclass: class name (renamed to myclass to avoid reserved name) in the xml file
        :param cmd: command to execute (from XML file)
        :return:
        """
        # only search if it isn't already in the cache
        if (myclass, cmd) in self.command_tuple_cache:
            return self.command_tuple_cache[(myclass, cmd)]

        # pick the right command file to draw from
        if (project == "ardrone3"):
            my_file = self.ardrone3_commands
        elif (project == "minidrone"):
            my_file = self.minidrone_commands
        else:
            my_file = self.common_commands

        # run the search first in minidrone xml and then hit common if that failed
        project_id = int(my_file.project['id'])

        for child in my_file.project.myclass:
            if child['name'] == myclass:
                class_id = int(child['id'])
                #print child['name']

                for subchild in child.cmd:
                    #print subchild
                    if subchild['name'] == cmd:
                        #print subchild['name']
                        cmd_id = int(subchild['id'])

                        # cache the result
                        self.command_tuple_cache[(myclass, cmd)] = (project_id, class_id, cmd_id)
                        return (project_id, class_id, cmd_id)



    def get_command_tuple_with_enum(self, project, myclass, cmd, enum_name):
        """
        Parses the command XML for the specified class name and command name and checks for enum_name

        :param myclass: class name (renamed to myclass to avoid reserved name) in the xml file
        :param cmd: command to execute (from XML file)
        :return:
        """
        # only search if it isn't already in the cache
        if (myclass, cmd, enum_name) in self.command_tuple_cache:
            #print("using the cache")
            #print(self.command_tuple_cache[(myclass, cmd, enum_name)])
            return self.command_tuple_cache[(myclass, cmd, enum_name)]

        # pick the right command file to draw from
        if (project == "ardrone3"):
            my_file = self.ardrone3_commands
        elif (project == "minidrone"):
            my_file = self.minidrone_commands
        else:
            my_file = self.common_commands

        # run the search first in minidrone xml and then hit common if that failed
        project_id = int(my_file.project['id'])

        for child in my_file.project.myclass:
            if child['name'] == myclass:
                class_id = int(child['id'])
                #print child['name']

                for subchild in child.cmd:
                    #print subchild
                    if subchild['name'] == cmd:
                        #print subchild['name']
                        cmd_id = int(subchild['id'])

                        for arg_child in subchild.arg:
                            if arg_child['type'] == "enum":
                                for e_idx, echild in enumerate(arg_child.enum):
                                    if echild['name'] == enum_name:
                                        enum_id = e_idx

                                        # cache the result
                                        self.command_tuple_cache[(myclass, cmd, enum_name)] = ((project_id, class_id, cmd_id), enum_id)

                                        #print  ((project_id, class_id, cmd_id), enum_id)
                                        return ((project_id, class_id, cmd_id), enum_id)

