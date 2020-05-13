import xml.etree.ElementTree as ET


def from_string(xml_data):
    if not xml_data:
        return None
    xml = XML()
    xml.data = ET.fromstring(f'<root> {"".join(xml_data)} </root>')
    return xml


def from_file(path):
    xml = XML()
    xml.data = ET.parse(path)
    return xml


class XML:
    def __init__(self):
        self.data = None
