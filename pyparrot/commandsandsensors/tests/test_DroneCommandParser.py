import unittest
from pyparrot.commandsandsensors import DroneCommandParser


class TestDroneCommandParser(unittest.TestCase):
    def test_get_command_tuple(self):
        cmd_parser = DroneCommandParser.DroneCommandParser()
        actual = cmd_parser.get_command_tuple("minidrone", "Piloting", "PCMD")
        expected = (2, 0, 2)
        self.assertEqual(expected, actual)

    def test_get_command_tuple_with_enum(self):
        cmd_parser = DroneCommandParser.DroneCommandParser()
        actual = cmd_parser.get_command_tuple_with_enum(
            "minidrone", "UsbAccessory", "ClawControl", "OPEN"
        )
        expected = ((2, 16, 1), 0)
        self.assertEqual(expected, actual)

    def test_minidrone(self):
        cmd_parser = DroneCommandParser.DroneCommandParser()
        actual = cmd_parser._load_xml("minidrone").getroot().get("id")
        expected = 2
        self.assertEqual(expected, int(actual))

    def test_ardrone3(self):
        cmd_parser = DroneCommandParser.DroneCommandParser()
        actual = cmd_parser._load_xml("ardrone3").getroot().get("id")
        expected = 1
        self.assertEqual(expected, int(actual))

    def test_common(self):
        cmd_parser = DroneCommandParser.DroneCommandParser()
        actual = cmd_parser._load_xml("common").getroot().get("id")
        expected = 0
        self.assertEqual(expected, int(actual))
