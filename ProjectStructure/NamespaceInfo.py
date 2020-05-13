from ProjectStructure.ObjectInfo import ObjectInfo
from Tools.Functions import parse_obj
from Tools.Regexes import NAME_REGEX
from Tools.Exceptions import WrongExpressionException

SEPARATORS = (' ', '.')


class NamespaceInfo(ObjectInfo):
    def __init__(self, father, namespace_strings, xml=None):
        super().__init__(father, xml)
        self.classes = []
        self.interfaces = []
        self.structs = []
        self.enums = []
        self.delegates = []

        self.get_namespace_info(namespace_strings, SEPARATORS)

    @parse_obj
    def get_namespace_info(self, args):
        pass

    def word_parser(self, word):
        if word == "namespace":
            if len(self.name) != 0:
                raise WrongExpressionException
        elif NAME_REGEX.match(word):
            self.name.append(word)
        else:
            raise WrongExpressionException

    def add_class(self, obj):
        print(f'class {"".join(obj.name)} added to namespace {self.name}')
        self.classes.append(obj)

    def add_namespace(self, obj):
        print(f"namespace {obj.name} added to namespace {self.name}")
        raise WrongExpressionException

    def add_enum(self, obj):
        print(f"enum {obj.name} added to namespace {self.name}")
        self.enums.append(obj)

    def add_interface(self, obj):
        print(f"interface {obj.name} added to namespace {self.name}")
        self.interfaces.append(obj)

    def add_struct(self, obj):
        print(f"struct {obj.name} added to namespace {self.name}")
        self.structs.append(obj)

    def add_delegate(self, obj):
        print(
            f'Delegate {"".join(obj.data_type)} {obj.name} added to namespace '
            f'{self.name}'
        )
        self.delegates.append(obj)
