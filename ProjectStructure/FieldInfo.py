from Tools.Enums import AccessModifiers
from ProjectStructure.ObjectInfo import ObjectInfo


class FieldInfo(ObjectInfo):
    def __init__(self, father, xml, acc_mod=AccessModifiers.Empty,
                 is_static=False, is_readonly=False, is_const=False,
                 data_type=None, name='', value=None, is_delegate=False):
        super().__init__(father, xml)
        if data_type is None:
            data_type = []
        self.access_modifier = acc_mod
        self.is_static = is_static
        self.is_readonly = is_readonly
        self.is_const = is_const
        self.data_type = data_type
        self.name = name
        self.value = value
        self.is_delegate = is_delegate
