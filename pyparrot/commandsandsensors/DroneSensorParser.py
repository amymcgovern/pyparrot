"""
Sensor parser class:  handles the XML parsing and gets the values but the actual data is stored with the drone itself
since it knows what to do with it.
"""
import struct
import untangle
from pyparrot.utils.colorPrint import color_print
import os
from os.path import join

def get_data_format_and_size(data, data_type):
    """
    Internal function to convert data_type to the corresponding struct.pack format string
    as per https://docs.python.org/2/library/struct.html#format-characters

    Function contributed by awm102 on GitHub.  Amy moved this to DroneSensorParser to be
    more general, edited a bit to fit within the drone sensor parser as well.

    :param data: the data that will be packed. Not actually used here unless the data_type is string, then
                 it is used to calculate the data size.
    :param data_type: a string representing the data type
    :return: a tuple of a string representing the struct.pack format for the data type and an int representing
             the number of bytes
    """

    if data_type == "u8" or data_type == "enum":
        format_char = "<B"
        data_size = 1
    elif data_type == "i8":
        format_char = "<b"
        data_size = 1
    elif data_type == "u16":
        format_char = "<H"
        data_size = 2
    elif data_type == "i16":
        format_char = "<h"
        data_size = 2
    elif data_type == "u32":
        format_char = "<I"
        data_size = 4
    elif data_type == "i32":
        format_char = "<i"
        data_size = 4
    elif data_type == "u64":
        format_char = "<Q"
        data_size = 8
    elif data_type == "i64":
        format_char = "<q"
        data_size = 8
    elif data_type == "float":
        format_char = "<f"
        data_size = 4
    elif data_type == "double":
        format_char = "<d"
        data_size = 8
    elif data_type == "string":
        format_char = "<s"
        data_size = len(data)
    else:
        format_char = ""
        data_size = 0

    return (format_char, data_size)


class DroneSensorParser:
    def __init__(self, drone_type):
        # grab module path per http://www.karoltomala.com/blog/?p=622
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)

        self.common_sensors = untangle.parse(join(dir_path, 'common.xml'))

        if (drone_type == "Minidrone"):
            self.drone_sensors = untangle.parse(join(dir_path, 'minidrone.xml'))
        else:
            self.drone_sensors = untangle.parse(join(dir_path, 'ardrone3.xml'))

        self.project_xmls = (self.drone_sensors, self.common_sensors)

        self.sensor_tuple_cache = dict()

    def extract_sensor_values(self, data):
        """
        Extract the sensor values from the data in the BLE packet
        :param data: BLE packet of sensor data
        :return: a list of tuples of (sensor name, sensor value, sensor enum, header_tuple)
        """
        sensor_list = []
        #print("updating sensors with ")
        try:
            header_tuple = struct.unpack_from("<BBH", data)
        except:
            color_print("Error: tried to parse a bad sensor packet", "ERROR")
            return None

        #print(header_tuple)
        (names, data_sizes) = self._parse_sensor_tuple(header_tuple)
        #print("name of sensor is %s" % names)
        #print("data size is %s" % data_sizes)

        packet_offset = 4
        if names is not None:
            for idx, name in enumerate(names):
                data_size = data_sizes[idx]
                try:
                    # figure out how to parse the data
                    (format_string, new_offset) = get_data_format_and_size(data[packet_offset:], data_size)

                    if (new_offset == 0):
                        # this is usually a boolean flag stating that values have changed so set the value to True
                        # and let it return the name
                        sensor_data = True
                    else:
                        # real data, parse it
                        sensor_data = struct.unpack_from(format_string, data, offset=packet_offset)
                        sensor_data = sensor_data[0]
                        if (data_size == "string"):
                            packet_offset += len(sensor_data)
                        else:
                            packet_offset += new_offset
                except Exception as e:
                    sensor_data = None
                    #print(header_tuple)
                    color_print("Error parsing data for sensor", "ERROR")
                    print(e)
                    print("name of sensor is %s" % names)
                    print("data size is %s" % data_sizes)
                    print(len(data))
                    print(4*(idx+1))

                #print("%s %s %s" % (name,idx,sensor_data))
                #color_print("updating the sensor!", "NONE")
                sensor_list.append([name, sensor_data, self.sensor_tuple_cache, header_tuple])

            return sensor_list

        else:
            color_print("Could not find sensor in list - ignoring for now.  Packet info below.", "ERROR")
            print(header_tuple)
            #print(names)
            return None

    def _parse_sensor_tuple(self, sensor_tuple):
        """
        Parses the sensor information from the command id bytes and returns the name
        of the sensor and the size of the data (so it can be unpacked properly)

        :param sensor_tuple: the command id tuple to be parsed (type, packet id, command tuple 3 levels deep)
        :return: a tuple with (name of the sensor, data size to be used for grabbing the rest of the data)
        """
        # grab the individual values
        (project_id, myclass_id, cmd_id) = sensor_tuple

        # return the cache if it is there
        if (project_id, myclass_id, cmd_id) in self.sensor_tuple_cache:
            return self.sensor_tuple_cache[(project_id, myclass_id, cmd_id)]

        for project_xml in self.project_xmls:
            #color_print("looking for project id %d in %s" % (project_id, project_xml))
            if (project_id == int(project_xml.project['id'])):
                #color_print("looking for myclass_id %d" % myclass_id)
                for c in project_xml.project.myclass:
                    #color_print("looking for cmd_id %d" % cmd_id)
                    if int(c['id']) == myclass_id:
                        for cmd_child in c.cmd:
                            if int(cmd_child['id']) == cmd_id:
                                cmd_name = cmd_child['name']
                                sensor_names = list()
                                data_sizes = list()

                                if (hasattr(cmd_child, 'arg')):
                                    for arg_child in cmd_child.arg:
                                        sensor_name = cmd_name + "_" + arg_child['name']
                                        data_size = arg_child['type']

                                        # special case, if it is an enum, need to add the enum mapping into the cache
                                        if (data_size == 'enum'):
                                            enum_names = list()
                                            for eitem in arg_child.enum:
                                                #color_print(eitem)
                                                enum_names.append(eitem['name'])
                                            self.sensor_tuple_cache[sensor_name, "enum"] = enum_names
                                            #color_print("added to sensor cache %s" % enum_names)

                                        # save the name and sizes to a list
                                        sensor_names.append(sensor_name)
                                        data_sizes.append(data_size)
                                else:
                                    # there is no sub-child argument meaning this is just a pure notification
                                    # special case values just use the command name and None for size
                                    sensor_names.append(cmd_name)
                                    data_sizes.append(None)

                                # cache the results
                                self.sensor_tuple_cache[(project_id, myclass_id, cmd_id)] = (
                                sensor_names, data_sizes)
                                return (sensor_names, data_sizes)


        # didn't find it, return an error
        # cache the results
        self.sensor_tuple_cache[(project_id, myclass_id, cmd_id)] = (None, None)
        return (None, None)
