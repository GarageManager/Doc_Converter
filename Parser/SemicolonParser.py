import ProjectStructure
from ProjectStructure.MethodInfo import MethodProperties
from Tools.Enums import AccessModifiers
from Tools.Regexes import NAME_REGEX, FUNC_REGEX
from Tools.Functions import (change_access_modifier,
                             is_access_modifier,
                             data_type_parser)
from Tools.Exceptions import (NotAMethodException,
                              NotAFieldException,
                              WrongExpressionException)
# TODO
method_type = {
    'delegate': False,
    'partial': False,
    'abstract': False,
    'virtual': False,
    'extern': False,
}
# TODO


class SemicolonParser:
    def __init__(self, father, strings, xml):
        self.father = father
        self.xml = xml
        self.strings = strings
        self.is_method = False
        self.is_field = False
        self.is_readonly = False
        self.is_static = False
        self.is_const = False
        self.is_delegate = False
        self.is_event = False
        self.name = ''
        self.value = []
        self.data_type = []
        self.access_modifier = AccessModifiers.Empty
        self.angle_brackets_count = 0
        self.method_properties = None

    def parse(self):
        for i in method_type:
            method_type[i] = False

        if isinstance(self.father, ProjectStructure.InterfaceInfo):
            self.method_properties = MethodProperties(
                self.access_modifier, self.is_static, method_type
            )
            return self.return_method(0, 0)

        for i in range(len(self.strings)):
            start = 0
            j = 0
            while j < len(self.strings[i]):
                if self.strings[i][j] == ' ':
                    if start != j:
                        self.word_parser(self.strings[i][start:j].strip())

                    if self.is_method:
                        return self.return_method(i, j + 1)
                    if self.is_event:
                        return self.return_event(self.strings)
                    if self.name:
                        return self.return_field(i, j)
                    start = j + 1

                if self.strings[i][j] == '(':
                    self.is_method = True
                    self.method_properties = MethodProperties(
                        self.access_modifier, self.is_static, method_type
                    )

                if self.strings[i][j] == '=':
                    if start != j:
                        self.word_parser(self.strings[i][start:j].strip())
                        j += 1
                    if self.name:
                        return self.return_field(i, j)
                    raise NotAFieldException
                j += 1

            if start != j:
                self.word_parser(self.strings[i][start:].strip())
                if self.is_method:
                    return self.return_method(i, j)
                if self.name:
                    return self.return_field(i, j)
        raise NotAFieldException

    def return_event(self, strings):
        return ProjectStructure.EventInfo(self.father, strings, self.xml)

    def return_field(self, str_num, pos):
        if not self.name or not self.data_type:
            raise NotAFieldException
        if self.is_delegate:
            return self.get_field_info()
        if self.strings[str_num][pos:]:
            self.value.append(self.strings[str_num][pos:])
            self.value.extend(self.strings[str_num + 1:])
        return self.get_field_info()

    def return_method(self, str_num, pos):
        self.method_properties.pos = [str_num, pos]
        try:
            method = ProjectStructure.MethodInfo(
                self.father,
                self.strings,
                self.xml,
                self.method_properties
            )
            return method
        except NotAMethodException:
            pass

    def is_func(self, word):
        if not self.is_field:
            if FUNC_REGEX.match(word):
                return True
        return False

    def word_parser(self, word):
        if word == 'using':
            raise NotAFieldException
        if is_access_modifier(word):
            self.access_modifier = change_access_modifier(self.access_modifier,
                                                          word)
            return

        if word == 'static':
            self.is_static = True
        elif word == 'const':
            self.is_const = True
        elif word == 'readonly':
            self.is_readonly = True
            self.is_field = True
        elif word == 'new':
            pass
        elif word == 'event':
            self.is_event = True
        elif word in method_type.keys():
            if not self.is_field:
                self.is_method = True
                method_type[word] = True
                self.method_properties = MethodProperties(
                    self.access_modifier, self.is_static, method_type
                )
            else:
                raise WrongExpressionException
        else:
            if self.is_func(word):
                self.is_delegate = True
            self.is_field = True
            pos, self.angle_brackets_count = data_type_parser(
                word, self.data_type, self.angle_brackets_count
            )

            if pos > len(word) - 1:
                return
            else:
                if not NAME_REGEX.match(word[pos:]):
                    raise NotAFieldException
                self.name = word[pos:]

    def get_field_info(self):
        return ProjectStructure.FieldInfo(
            self.father,
            self.xml,
            self.access_modifier,
            self.is_static,
            self.is_readonly,
            self.is_const,
            self.data_type,
            self.name,
            self.value,
            self.is_delegate
        )
