from ProjectStructure.ObjectInfo import ObjectInfo
from Tools.Enums import AccessModifiers
from Tools.Exceptions import WrongExpressionException
from Tools.Functions import (change_access_modifier, is_access_modifier,
                             parse_obj)
from Tools.Regexes import NAME_REGEX

SEPARATORS = (' ', ':')


class StructInfo(ObjectInfo):
    def __init__(self, father, struct_str, xml=None):
        super().__init__(father, xml)
        self.access_modifier = AccessModifiers.Empty
        self.is_static = False
        self.is_readonly = False
        self.is_const = False
        self.rest_of_string = []

        self.classes = []
        self.interfaces = []
        self.structs = []
        self.enums = []
        self.fields = []
        self.methods = []
        self.delegates = []
        self.properties = []

        self.get_struct_info(struct_str, SEPARATORS)

    @parse_obj
    def get_struct_info(self, args):
        if self.name:
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
        elif word == "struct":
            if self.name:
                raise WrongExpressionException
        elif word == "static":
            self.is_static = True
        elif word == "readonly":
            self.is_readonly = True
        elif word == "const":
            self.is_const = True
        else:
            if NAME_REGEX.match(word):
                self.name = word
            else:
                raise WrongExpressionException

    def add_class(self, obj):
        self.classes.append(obj)

    def add_namespace(self, obj):
        raise WrongExpressionException

    def add_enum(self, obj):
        self.enums.append(obj)

    def add_interface(self, obj):
        self.interfaces.append(obj)

    def add_struct(self, obj):
        self.structs.append(obj)

    def add_field(self, obj):
        if obj.value:
            raise WrongExpressionException
        self.fields.append(obj)

    def add_method(self, obj):
        self.methods.append(obj)

    def add_delegate(self, obj):
        self.delegates.append(obj)

    def add_property(self, obj):
        self.properties.append(obj)
