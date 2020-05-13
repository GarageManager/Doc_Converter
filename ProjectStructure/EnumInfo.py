from Tools.Enums import AccessModifiers
from Tools.Exceptions import WrongExpressionException
from Tools.Functions import (is_access_modifier, change_access_modifier,
                             parse_obj)
from Tools.Regexes import NAME_REGEX
from ProjectStructure.ObjectInfo import ObjectInfo

SEPARATORS = (' ',)


class EnumInfo(ObjectInfo):
    def __init__(self, father, enum_str, xml=None):
        super().__init__(father, xml)
        self.access_modifier = AccessModifiers.Empty
        self.is_static = False
        self.enum_fields = []
        self.rest_of_string = []

        self.get_enum_info(enum_str, SEPARATORS)

    @parse_obj
    def get_enum_info(self, args):
        if self.rest_of_string:
            self.rest_of_string.append(
                args.strings[args.str_num][args.pos + 1:]
            )
            self.rest_of_string.extend(args.strings[args.str_num + 1:])
            return True
        return False

    def word_parser(self, word):
        if is_access_modifier(word):
            self.access_modifier = change_access_modifier(self.access_modifier,
                                                          word)
        elif word == "enum":
            if self.name:
                raise WrongExpressionException
        elif word == "static":
            self.is_static = True
        elif NAME_REGEX.match(word):
            self.name = word

    # def add_fields(self, fields):
    #     self.fields = fields

    def add_enum_field(self, obj):
        self.enum_fields.append(obj)
