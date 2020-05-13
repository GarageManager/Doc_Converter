import re

IS_NAMESPACE_REGEX = re.compile('(?<!\w)namespace(?!\w)')
IS_CLASS_REGEX = re.compile('(?<!\w)class(?!\w)')
IS_STRUCT_REGEX = re.compile('(?<!\w)struct(?!\w)')
IS_INTERFACE_REGEX = re.compile('(?<!\w)interface(?!\w)')
IS_ENUM_REGEX = re.compile('(?<!\w)enum(?!\w)')
IS_ATTRIBUTE_REGEX = re.compile('^\s*\[[\w\W]*$')
SET_REGEX = re.compile('[\s]*(?<!\w)set(?!\w)')
GET_REGEX = re.compile('[\s]*(?<!\w)get(?!\w)')

# if string starts with 'Func' then it's delegate
FUNC_REGEX = re.compile('^Func[^\w]')
# names can only contains letters, digits and '_'
NAME_REGEX = re.compile('^[a-zA-Z_]\w*$')
# data types can only contains letters, digits and '_< >,.[]'
DATA_TYPE_REGEX1 = re.compile('^[a-zA-Z_][\w.,: _<>\[\]]*[\s\w]*$')
DATA_TYPE_REGEX2 = re.compile('^[a-zA-Z_., <>\[\]][\w.,: _<>\[\]]*$')
# if string contains '=' then it's not a method and probably it's a field
IS_FIELD_REGEX = re.compile('[\w ]*(=)(?![^\w ])')
# property names can only contains letters, digits and '.,: _<>[]'
PROPERTY_NAME_REGEX1 = re.compile('^[a-zA-Z_][\w.,: _<>\[\]]*$')
PROPERTY_NAME_REGEX2 = re.compile('^[a-zA-Z_., <>\[\]][\w.,: _<>\[\]]*$')
