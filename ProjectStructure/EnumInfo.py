from Parser.XmlParser import from_string
from Tools.Enums import AccessModifiers
from Tools.Exceptions import WrongExpressionException
from Tools.Functions import (is_access_modifier, change_access_modifier,
                             parse_obj)
from Tools.Regexes import NAME_REGEX
from ProjectStructure.ObjectInfo import ObjectInfo

SEPARATORS = (' ', ':')


class EnumInfo(ObjectInfo):
    def __init__(self, father, enum_str, xml=None):
        super().__init__(father, xml)
        self.access_modifier = AccessModifiers.Empty
        self.is_static = False
        self.enum_fields = []
        self.inheritance = []

        self.get_enum_info(enum_str, SEPARATORS)

    @parse_obj
    def get_enum_info(self, args):
        pass

    def word_parser(self, word):
        if is_access_modifier(word):
            self.access_modifier = change_access_modifier(self.access_modifier,
                                                          word)
        elif word == "enum":
            if self.name:
                raise WrongExpressionException
        elif word == "static":
            self.is_static = True
        elif not self.name:
            if NAME_REGEX.match(word):
                self.name = word
            else:
                raise WrongExpressionException
        else:
            self.inheritance.append(word)

    def add_enum_field(self, xml, obj):
        self.enum_fields.append((from_string(xml), obj))
