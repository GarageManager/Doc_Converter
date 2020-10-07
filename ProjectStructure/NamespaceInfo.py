from ProjectStructure.ObjectInfo import ObjectInfo
from Tools.Functions import parse_obj
from Tools.Regexes import NAMESPACE_REGEX1, NAMESPACE_REGEX2
from Tools.Exceptions import WrongExpressionException

SEPARATORS = (' ', )


class NamespaceInfo(ObjectInfo):
    def __init__(self, father, namespace_strings, xml=None):
        super().__init__(father, xml)
        self._get_namespace_info(namespace_strings, SEPARATORS)
        self.name = ''.join(self.name)

    @parse_obj
    def _get_namespace_info(self, args):
        pass

    def word_parser(self, word):
        if word == "namespace":
            if self.name:
                raise WrongExpressionException
        elif not self.name:
            if NAMESPACE_REGEX1.match(word):
                self.name.append(word)
            else:
                raise WrongExpressionException
        else:
            if NAMESPACE_REGEX2.match(word):
                self.name.append(word)
            else:
                raise WrongExpressionException

    def add_class(self, obj):
        self.classes.append(obj)

    def add_namespace(self, obj):
        self.namespaces.append(obj)

    def add_enum(self, obj):
        self.enums.append(obj)

    def add_interface(self, obj):
        self.interfaces.append(obj)

    def add_struct(self, obj):
        self.structs.append(obj)

    def add_delegate(self, obj):
        self.delegates.append(obj)
