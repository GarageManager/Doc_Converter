from ProjectStructure.ObjectInfo import ObjectInfo
from Tools.Enums import AccessModifiers
from Tools.Exceptions import NotAPropertyException
from Tools.Functions import (change_access_modifier, is_access_modifier,
                             parse_obj, data_type_parser)
from Tools.Regexes import PROPERTY_NAME_REGEX1, PROPERTY_NAME_REGEX2

SEPARATORS = (' ',)


class PropertyInfo(ObjectInfo):
    def __init__(self, father, xml, property_str):
        super().__init__(father, xml)
        self.data_type = []
        self.access_modifier = AccessModifiers.Empty
        self.is_static = False
        self.get_value = []
        self.set_value = []

        self.get_set_flag = False  # need to rename
        self.angle_brackets_count = 0
        self.get_property_info(property_str, SEPARATORS)

    @parse_obj
    def get_property_info(self, args):
        pass

    def word_parser(self, word):
        if is_access_modifier(word):
            self.access_modifier = change_access_modifier(self.access_modifier,
                                                          word)
            return
        elif word == "static":
            self.is_static = True
            return
        if word == 'new':
            return
        pos, self.angle_brackets_count = data_type_parser(
            word, self.data_type, self.angle_brackets_count
        )
        if pos > len(word) - 1:
            return
        else:
            if not self.name:
                if not PROPERTY_NAME_REGEX1.match(word[pos:]):
                    raise NotAPropertyException  # Maybe WrongExpr
                self.name.append(word[pos:])
            else:
                if not PROPERTY_NAME_REGEX2.match(word[pos:]):
                    raise NotAPropertyException  # Maybe WrongExpr
                self.name.append(word[pos:])

    def add_set_value(self, value):
        self.set_value = [x for x in value]

    def add_get_value(self, value):
        self.get_value = [x for x in value]

    def add_value(self, value):
        if not self.get_value:
            self.get_value = [x for x in value]
        else:
            self.set_value = [x for x in value]
