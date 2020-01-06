import os
import xml.etree.ElementTree as et
from os.path import join
from typing import Tuple


class DroneCommandParser:
    def __init__(self):
        # parse the command files from XML (so we don't have to store ids and can use names
        # for readability and portability!)
        self.xmls = {}

    def _load_xml(self, project: str) -> et.ElementTree:
        if project not in self.xmls:
            # grab module path per http://www.karoltomala.com/blog/?p=622
            path = os.path.abspath(__file__)
            dir_path = os.path.dirname(path)
            self.xmls[project] = et.parse(join(dir_path, f"{project}.xml"))
        return self.xmls[project]

    def get_command_tuple(
        self, project: str, myclass: str, cmd: str
    ) -> Tuple[int, int, int]:
        """
        Parses the command XML for the specified class name and command name

        :param myclass: class name (renamed to myclass to avoid reserved name) in the xml file
        :param cmd: command to execute (from XML file)
        :return:
        """

        # pick the right command file to draw from
        xml = self._load_xml(project)
        project_id = xml.getroot().get("id")
        class_id = xml.find(f"myclass[@name='{myclass}']").get("id")
        cmd_id = xml.find(f"myclass[@name='{myclass}']/cmd[@name='{cmd}']").get("id")
        return (int(project_id), int(class_id), int(cmd_id))

    def get_command_tuple_with_enum(
        self, project: str, myclass: str, cmd: str, enum_name: str
    ) -> Tuple[Tuple[int, int, int], int]:
        """
        Parses the command XML for the specified class name and command name and checks for enum_name

        :param myclass: class name (renamed to myclass to avoid reserved name) in the xml file
        :param cmd: command to execute (from XML file)
        :return:
        """

        # pick the right command file to draw from
        xml = self._load_xml(project)
        (project_id, class_id, cmd_id) = self.get_command_tuple(project, myclass, cmd)
        arg_enum_node = xml.find(
            f"myclass[@name='{myclass}']/cmd[@name='{cmd}']/arg[@type='enum']"
        )
        enum_id = list(arg_enum_node).index(
            arg_enum_node.find(f"enum[@name='{enum_name}']")
        )
        return ((project_id, class_id, cmd_id), enum_id)
