from ProjectStructure.ObjectInfo import ObjectInfo
from Tools.Enums import AccessModifiers
from Tools.Exceptions import NotAPropertyException
from Tools.Functions import (change_access_modifier, is_access_modifier,
                             parse_obj, data_type_parser)
from Tools.Regexes import PROPERTY_NAME_REGEX1, PROPERTY_NAME_REGEX2

SEPARATORS = (' ',)


class PropertyInfo(ObjectInfo):
    def __init__(self, father, property_str, xml):
        super().__init__(father, xml)
        self.data_type = []
        self.access_modifier = AccessModifiers.Empty
        self.is_static = False
        self.is_virtual = False
        self.is_abstract = False
        self.is_override = False
        self.is_indexer = False
        self.private_get = False
        self.private_set = False
        self.has_get_value = False
        self.has_set_value = False

        self._is_private = False
        self.curly_brackets_count = 1  # TODO
        self._angle_brackets_count = 0
        self.get_property_info(property_str, SEPARATORS)
        self.name = ' '.join(self.name)

    @parse_obj
    def get_property_info(self, args):
        pass

    def word_parser(self, word):
        if word == 'new':
            return
        if is_access_modifier(word):
            self.access_modifier = change_access_modifier(self.access_modifier,
                                                          word)
        elif word == "static":
            self.is_static = True
        elif word == 'override':
            self.is_override = True
        elif word == 'abstract':
            self.is_abstract = True
        elif word == 'virtual':
            self.is_virtual = True
        else:
            pos, self._angle_brackets_count = data_type_parser(
                word, self.data_type, self._angle_brackets_count
            )
            if pos > len(word) - 1:
                return
            else:
                if not self.name:
                    if not PROPERTY_NAME_REGEX1.match(word[pos:]):
                        raise NotAPropertyException
                    _word = word[pos:]
                    if 'this' in _word:
                        self.is_indexer = True
                    self.name.append(_word)
                else:
                    if not PROPERTY_NAME_REGEX2.match(word[pos:]):
                        raise NotAPropertyException
                    self.name.append(word[pos:])

    def parse_property_body(self, args):
        if args.char == '{':
            self.curly_brackets_count += 1
        elif args.char == '}':
            self.curly_brackets_count -= 1

        if self.curly_brackets_count == 1:
            if (len(args.line) - args.pos > 6
                    and args.line[args.pos:args.pos + 7] == 'private'):
                self._is_private = True
            elif (
                    len(args.line) - args.pos > 2 and
                    args.line[args.pos:args.pos + 3] in ['get', 'set'] and
                    (len(args.line) - 3 == args.pos or
                     args.line[args.pos + 3] in ['{', ' ', ';'])
            ):
                if args.char == 'g':
                    if self._is_private:
                        self._is_private = False
                        self.private_get = True
                    self.has_get_value = True
                else:
                    if self._is_private:
                        self._is_private = False
                        self.private_set = True
                    self.has_set_value = True

    # def parse_body(self, char):


    # def add_set_value(self, value):
    #     self.set_value = [x for x in value]

    # def add_get_value(self, value):
    #     self.get_value = [x for x in value]

    # def add_value(self, value):
    #     if not self.get_value:
    #         self.get_value = [x for x in value]
    #     else:
    #         self.set_value = [x for x in value]
