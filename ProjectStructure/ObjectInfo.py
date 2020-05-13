from Tools.Exceptions import WrongExpressionException
from Parser.XmlParser import from_string


class ObjectInfo:
    def __init__(self, father=None, xml=None):
        self.father = father
        self.xml = from_string(xml)
        self.name = []

        self.namespaces = []
        self.classes = []
        self.interfaces = []
        self.structs = []
        self.enums = []
        self.fields = []
        self.methods = []
        self.delegates = []
        self.properties = []

    def add_class(self, obj):
        raise WrongExpressionException

    def add_namespace(self, obj):
        raise WrongExpressionException

    def add_enum(self, obj):
        raise WrongExpressionException

    def add_interface(self, obj):
        raise WrongExpressionException

    def add_struct(self, obj):
        raise WrongExpressionException

    def add_field(self, obj):
        raise WrongExpressionException

    def add_method(self, obj):
        raise WrongExpressionException

    def add_delegate(self, obj):
        raise WrongExpressionException

    def add_property(self, obj):
        raise WrongExpressionException

    # def __str__(self):
    #     counter = 0
    #     father = self.father
    #     while father:
    #         father = father.father
    #         counter += 2
    #
    #     name = ' '.join(self.name) if type(self.name) == list else self.name
    #
    #     strings = [f'{"  " * counter}{name}\n', ]
    #     counter += 1
    #
    #     if self.namespaces:
    #         strings.append(f'{"  " * counter}Classes:\n')
    #         for i in self.namespaces:
    #             strings.append(str(i))
    #     if self.classes:
    #         strings.append(f'{"  " * counter}Classes:\n')
    #         for i in self.classes:
    #             strings.append(str(i))
    #     if self.interfaces:
    #         strings.append(f'{"  " * counter}Interfaces:\n')
    #         for i in self.interfaces:
    #             strings.append(str(i))
    #     if self.structs:
    #         strings.append(f'{"  " * counter}Structs:\n')
    #         for i in self.structs:
    #             strings.append(str(i))
    #     if self.enums:
    #         strings.append(f'{"  " * counter}Enums:\n')
    #         for i in self.enums:
    #             strings.append(str(i))
    #     if self.properties:
    #         strings.append(f'{"  " * counter}Properties:\n')
    #         for i in self.properties:
    #             strings.append(str(i))
    #     if self.fields:
    #         strings.append(f'{"  " * counter}Fields:\n')
    #         for i in self.fields:
    #             strings.append(str(i))
    #     if self.methods:
    #         strings.append(f'{"  " * counter}Methods:\n')
    #         for i in self.methods:
    #             strings.append(str(i))
    #     if self.delegates:
    #         strings.append(f'{"  " * counter}Delegates:\n')
    #         for i in self.delegates:
    #             strings.append(str(i))
    #
    #     return ''.join(strings)
