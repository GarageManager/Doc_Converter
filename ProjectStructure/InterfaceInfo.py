from ProjectStructure.ObjectInfo import ObjectInfo
from Tools.Enums import AccessModifiers
from Tools.Exceptions import WrongExpressionException
from Tools.Functions import (get_generic_info, parse_obj, is_access_modifier,
                             change_access_modifier, data_type_parser)

SEPARATORS = (' ', ':')


class InterfaceInfo(ObjectInfo):
    def __init__(self, father, interface_str, xml=None):
        super().__init__(father, xml)
        self.access_modifier = AccessModifiers.Empty
        self.is_partial = False
        self.rest_of_string = []
        self.generic_info = []

        self.classes = []
        self.interfaces = []
        self.structs = []
        self.enums = []
        self.methods = []
        self.delegates = []
        self.properties = []

        self._angle_brackets_count = 0
        self.get_interface_info(interface_str, SEPARATORS)
        get_generic_info(self)

    @parse_obj
    def get_interface_info(self, args):
        if len(self.rest_of_string) != 0:
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
        elif word == 'interface':
            if len(self.name) != 0:
                raise WrongExpressionException
        elif word == 'partial':
            self.is_partial = True
        else:
            pos, self._angle_brackets_count = data_type_parser(
                word, self.name, self._angle_brackets_count
            )
            if pos < len(word):
                self.rest_of_string.append(word[pos:])

    def add_class(self, obj):
        print(f'class {"".join(obj.name)} added to interface '
              f'{"".join(self.name)}')
        self.classes.append(obj)

    def add_enum(self, obj):
        print(f'enum {"".join(obj.name)} added to interface '
              f'{"".join(self.name)}')
        self.enums.append(obj)

    def add_interface(self, obj):
        print(f'interface {"".join(obj.name)} added to interface '
              f'{"".join(self.name)}')
        self.interfaces.append(obj)

    def add_struct(self, obj):
        print(f'struct {"".join(obj.name)} added to interface '
              f'{"".join(self.name)}')
        self.structs.append(obj)

    def add_field(self, obj):
        raise WrongExpressionException

    def add_method(self, obj):
        print(f'method {"".join(obj.name)} added to interface '
              f'{"".join(self.name)}')
        self.methods.append(obj)

    def add_delegate(self, obj):
        print(
            f'Delegate {"".join(obj.data_type)} {obj.name} added to class '
            f'{"".join(self.name)}'
        )
        self.delegates.append(obj)

    def add_property(self, obj):
        print(f'Property {"".join(obj.name)} added to class '
              f'{"".join(self.name)}')
        self.properties.append(obj)