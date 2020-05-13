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
            if self.name:
                raise WrongExpressionException
        elif NAME_REGEX.match(word):
            self.name.append(word)
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

    def add_delegate(self, obj):
        self.delegates.append(obj)
