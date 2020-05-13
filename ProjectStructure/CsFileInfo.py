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
        print(f'class {"".join(obj.name)} added to file {"".join(self.name)}')
        self.classes.append(obj)

    def add_namespace(self, obj):
        print(f'namespace {".".join(obj.name)} added to file '
              f'{"".join(self.name)}')
        self.namespaces.append(obj)

    def add_enum(self, obj):
        print(f'enum {"".join(obj.name)} added to file {"".join(self.name)}')
        self.enums.append(obj)

    def add_interface(self, obj):
        print(f'interface {"".join(obj.name)} added to file '
              f'{"".join(self.name)}')
        self.interfaces.append(obj)

    def add_struct(self, obj):
        print(f'struct {"".join(obj.name)} added to file {"".join(self.name)}')
        self.structs.append(obj)

    def add_delegate(self, obj):
        print(
            f'Delegate {"".join(obj.data_type)} {obj.name} added to file '
            f'{"".join(self.name)}'
        )
        self.delegates.append(obj)
