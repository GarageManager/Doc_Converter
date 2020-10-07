import re

IS_NAMESPACE_REGEX = re.compile(r'(?<!\w)namespace(?!\w)')
IS_EVENT_REGEX = re.compile(r'(?<!\w)event(?!\w)')
IS_CLASS_REGEX = re.compile(r'(?<!\w)class(?!\w)')
IS_STRUCT_REGEX = re.compile(r'(?<!\w)struct(?!\w)')
IS_INTERFACE_REGEX = re.compile(r'(?<!\w)interface(?!\w)')
IS_ENUM_REGEX = re.compile(r'(?<!\w)enum(?!\w)')
IS_ATTRIBUTE_REGEX = re.compile(r'^\s*\[[\w\W]*$')
SET_REGEX = re.compile(r'[\s]*(?<!\w)set(?!\w)')
GET_REGEX = re.compile(r'[\s]*(?<!\w)get(?!\w)')

NAMESPACE_REGEX1 = re.compile(r'^[a-zA-Z_][\w.]*$')
NAMESPACE_REGEX2 = re.compile(r'^[a-zA-Z_.][\w.]*$')
# if string starts with 'Func' then it's delegate
FUNC_REGEX = re.compile(r'^Func[^\w]')
# names can only contains letters, digits and '_'
NAME_REGEX = re.compile(r'^[a-zA-Z_]\w*$')
# data types can only contains letters, digits and '_< >,.[]'
DATA_TYPE_REGEX1 = re.compile(r'^[a-zA-Z_][\w.,: _<>\[\]]*[\s\w]*$')
DATA_TYPE_REGEX2 = re.compile(r'^[a-zA-Z_., <>\[\]][\w.,: _<>\[\]]*$')
# if string contains '=' then it's not a method and probably it's a field
IS_FIELD_REGEX = re.compile(r'[\w ]*(=)(?![^\w ])')
# property names can only contains letters, digits and '.,: _<>[]'
PROPERTY_NAME_REGEX1 = re.compile(r'^[a-zA-Z_][\w.,: _<>\[\]]*$')
PROPERTY_NAME_REGEX2 = re.compile(r'^[a-zA-Z_., <>\[\]][\w.,: _<>\[\]]*$')

GET_FONTS_INFO = re.compile(r'(5 0 obj[\w\W]*)(?:2 0 obj)')
GET_OBJECTS = re.compile(r'((?<=\w 0 obj\s)[\w\W]*?)\s*endobj|(\w+ 0 obj)')

XML_SPACE_REPLACE = re.compile(r'\s+')
