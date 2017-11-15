"""
Sensor parser class:  handles the XML parsing and gets the values but the actual data is stored with the drone itself
since it knows what to do with it.
"""
import struct
import untangle
from utils.colorPrint import color_print
import os
from os.path import join

class DroneSensorParser:
    def __init__(self, drone_type):
        # grab module path per http://www.karoltomala.com/blog/?p=622
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)

        self.common_sensors = untangle.parse(join(dir_path, 'common.xml'))

        if (drone_type == "Mambo"):
            self.drone_sensors = untangle.parse(join(dir_path, 'minidrone.xml'))
        else:
            self.drone_sensors = untangle.parse(join(dir_path, 'ardrone3.xml'))

        self.sensor_tuple_cache = dict()

    def extract_sensor_values(self, data):
        """
        Extract the sensor values from the data in the BLE packet
        :param data: BLE packet of sensor data
        :return: a tuple of (sensor name, sensor value, sensor enum, header_tuple)
        """
        #print("updating sensors with ")
        header_tuple = struct.unpack_from("<BBBB", data)
        #print(header_tuple)
        (names, data_sizes) = self._parse_sensor_tuple(header_tuple)
        #print "name of sensor is %s" % names
        #print "data size is %s" % data_sizes

        if names is not None:
            for idx, name in enumerate(names):
                data_size = data_sizes[idx]

                if (data_size == "u8" or data_size == "enum"):
                    # unsigned 8 bit, single byte
                    sensor_data = struct.unpack_from("<B", data, offset=4)
                    sensor_data = int(sensor_data[0])
                elif (data_size == "i8"):
                    # signed 8 bit, single byte
                    sensor_data = struct.unpack_from("<b", data, offset=4)
                    sensor_data = int(sensor_data[0])
                elif (data_size == "u16"):
                    sensor_data = struct.unpack_from("<H", data, offset=4)
                    sensor_data = int(sensor_data[0])
                elif (data_size == "i16"):
                    sensor_data = struct.unpack_from("<h", data, offset=4)
                    sensor_data = int(sensor_data[0])
                elif (data_size == "u32"):
                    sensor_data = struct.unpack_from("<I", data, offset=4)
                    sensor_data = int(sensor_data[0])
                elif (data_size == "i32"):
                    sensor_data = struct.unpack_from("<i", data, offset=4)
                    sensor_data = int(sensor_data[0])
                elif (data_size == "u64"):
                    sensor_data = struct.unpack_from("<Q", data, offset=4)
                    sensor_data = int(sensor_data[0])
                elif (data_size == "i64"):
                    sensor_data = struct.unpack_from("<q", data, offset=4)
                    sensor_data = int(sensor_data[0])
                elif (data_size == "float"):
                    sensor_data = struct.unpack_from("<f", data, offset=4)
                    sensor_data = float(sensor_data[0])
                elif (data_size == "double"):
                    sensor_data = struct.unpack_from("<d", data, offset=4)
                    sensor_data = float(sensor_data[0])
                elif (data_size == "string"):
                    # string
                    sensor_data = struct.unpack_from("<s", data, offset=4)
                    sensor_data = sensor_data[0]
                else:
                    sensor_data = None
                    color_print("Write the parser for this value", "ERROR")

                #color_print("updating the sensor!", "NONE")

                return (name, sensor_data, self.sensor_tuple_cache, header_tuple)
        else:
            color_print("Error parsing sensor information!", "ERROR")
            print(header_tuple)
            return (None, None, None, None)


    def _parse_sensor_tuple(self, sensor_tuple):
        """
        Parses the sensor information from the command id bytes and returns the name
        of the sensor and the size of the data (so it can be unpacked properly)

        :param sensor_tuple: the command id tuple to be parsed (type, packet id, command tuple 3 levels deep)
        :return: a tuple with (name of the sensor, data size to be used for grabbing the rest of the data)
        """
        # grab the individual values
        (project_id, myclass_id, cmd_id, extra_id) = sensor_tuple

        # return the cache if it is there
        if (project_id, myclass_id, cmd_id, extra_id) in self.sensor_tuple_cache:
            return self.sensor_tuple_cache[(project_id, myclass_id, cmd_id, extra_id)]

        #color_print("looking for project id %d in minidrone" % project_id)
        if (project_id == int(self.drone_sensors.project['id'])):
            #color_print("looking for myclass_id %d" % myclass_id)
            for c in self.drone_sensors.project.myclass:
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
                                            color_print(eitem)
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
                            self.sensor_tuple_cache[(project_id, myclass_id, cmd_id, extra_id)] = (
                            sensor_names, data_sizes)
                            return (sensor_names, data_sizes)

        # need to look in the common.xml file instead
        #color_print("looking for project id %d in common" % project_id)
        if (project_id == int(self.common_sensors.project['id'])):
            #color_print("looking for myclass_id %d" % myclass_id)
            for c in self.common_sensors.project.myclass:
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
                                            color_print(eitem)
                                            enum_names.append(eitem['name'])
                                        self.sensor_tuple_cache[sensor_name, "enum"] = enum_names
                                        #color_print("added to sensor cache %s" % enum_names, 1)

                                    # save the name and sizes to a list
                                    sensor_names.append(sensor_name)
                                    data_sizes.append(data_size)
                            else:
                                # there is no sub-child argument meaning this is just a pure notification
                                # special case values just use the command name and None for size
                                sensor_names.append(cmd_name)
                                data_sizes.append(None)

                            # cache the results
                            self.sensor_tuple_cache[(project_id, myclass_id, cmd_id, extra_id)] = (
                            sensor_names, data_sizes)
                            return (sensor_names, data_sizes)

        # didn't find it, return an error
        # cache the results
        self.sensor_tuple_cache[(project_id, myclass_id, cmd_id, extra_id)] = (None, None)
        return (None, None)
