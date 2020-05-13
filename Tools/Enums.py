from enum import Enum


class AccessModifiers(Enum):
    Public = 0
    Private = 1
    Protected = 2
    Internal = 3
    ProtectedInternal = 4
    PrivateProtected = 5
    Empty = 6


class Fathers(Enum):
    Namespace = 0
    Class = 1
    Struct = 2
    Interface = 3
    Enum = 4
    File = 5
