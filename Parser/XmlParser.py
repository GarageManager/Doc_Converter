import xml.etree.ElementTree as ET
from Tools.Regexes import XML_SPACE_REPLACE as regex


class XMLElements:
    def __init__(self):
        self.tag = ''
        self.attributes = {}
        self.data = []


def from_string(xml_data):
    if not xml_data:
        return None
    return list(
        get_formatted_xml(ET.fromstring(f'<root> {"".join(xml_data)} </root>'))
    )


def from_file(path):
    return ET.parse(path)


def get_formatted_xml(xml):
    res = None
    for item in xml:
        res = XMLElements()
        res.tag = item.tag
        if item.attrib:
            res.attributes = item.attrib
        if item.text and item.text.strip():
            res.data.append(regex.sub(' ', item.text.strip()))
        res.data.extend(get_formatted_xml(item))
        if item.tail and item.tail.strip():
            res.data.append(regex.sub(' ', item.tail.strip()))
        yield res
    return res
