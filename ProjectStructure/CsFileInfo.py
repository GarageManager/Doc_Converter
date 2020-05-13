from ProjectStructure.ObjectInfo import ObjectInfo


class FileInfo(ObjectInfo):
    def __init__(self, filename):
        super().__init__()
        self.name = filename
        self.namespaces = []
        self.modules = []
        self.enums = []
        self.classes = []
        self.interfaces = []
        self.structs = []
        self.delegates = []

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
