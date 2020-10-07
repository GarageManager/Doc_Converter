from enum import Enum


class Fonts(Enum):
    CodeBlock = 0,
    CodeBlockDefault = 1,
    CodeBlockName = 2,
    Filename = 3,
    Title = 4,
    Item = 5,
    ObjectName = 6,
    Default = 7,
    DefaultBold = 8,
    XMLTitle = 9,
    Subtitle = 10,
    XMLLink = 11,
    XMLName = 12,
    PageNumber = 13


class AccessModifiers(Enum):
    Public = 0
    Private = 1
    Protected = 2
    Internal = 3
    ProtectedInternal = 4
    PrivateProtected = 5
    Empty = 6
