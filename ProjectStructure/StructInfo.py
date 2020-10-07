from ProjectStructure.ObjectInfo import ObjectInfo
from Tools.Enums import AccessModifiers
from Tools.Exceptions import WrongExpressionException
from Tools.Functions import (change_access_modifier, is_access_modifier,
                             parse_obj, get_generic_info)
from Tools.Regexes import NAME_REGEX

SEPARATORS = (' ', ':')


class StructInfo(ObjectInfo):
    def __init__(self, father, struct_str, xml=None):
        super().__init__(father, xml)
        self.access_modifier = AccessModifiers.Empty
        self.is_static = False
        self.is_readonly = False
        self.is_const = False
        self.generic_info = []

        self.get_struct_info(struct_str, SEPARATORS)
        get_generic_info(self)
        self.name = ''.join(self.name)

    @parse_obj
    def get_struct_info(self, args):
        pass

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
        elif not self.name:
            if NAME_REGEX.match(word):
                self.name.append(word)
            else:
                raise WrongExpressionException
        else:
            self.inheritance.append(word)

    def add_class(self, obj):
        self.classes.append(obj)

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

    def add_event(self, obj):
        self.events.append(obj)

    def add_constructor(self, obj):
        self.constructors.append(obj)
