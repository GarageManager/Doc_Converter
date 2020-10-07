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
        self.constructors = []
        self.methods = []
        self.delegates = []
        self.properties = []
        self.events = []

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

    def add_event(self, obj):
        raise WrongExpressionException

    def add_constructor(self, obj):
        raise WrongExpressionException
