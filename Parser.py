from logger_configuration import logger
import xml.etree.ElementTree as ETree
from collections import namedtuple

ComputerData = namedtuple("ComputerData", ["agent_name", "ip", "port", "computer_name"])


def parse_config_file(ip_address_dict):
    xml_root_tree = ETree.parse('network_def.xml').getroot()
    for agent in xml_root_tree:
        if agent.tag == "agent":
            ip_address_dict[agent.attrib["ip"]] = ComputerData(agent.attrib["agent_name"],
                                                               agent.attrib["ip"],
                                                               agent.attrib["port"],
                                                               agent.attrib["computer_name"])
