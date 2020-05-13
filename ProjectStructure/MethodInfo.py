from ProjectStructure.ObjectInfo import ObjectInfo
from Tools.Enums import AccessModifiers
from Tools.Functions import (data_type_parser, is_operator, parse_brackets,
                             change_access_modifier, is_access_modifier)
from Tools.Classes import Bracket
from Tools.Exceptions import NotAMethodException, WrongExpressionException
from ProjectStructure.ClassInfo import ClassInfo
from ProjectStructure.StructInfo import StructInfo
from Tools.Regexes import DATA_TYPE_REGEX1, DATA_TYPE_REGEX2


class MethodProperties:
    def __init__(
            self,
            access_modifier=AccessModifiers.Empty,
            is_static=False,
            method_type=None,
            pos=None,
    ):
        self.name = []
        self.access_modifier = access_modifier
        self.is_static = is_static
        if pos is None:
            pos = [0, 0]
        if method_type is not None:
            self.is_delegate = method_type['delegate']
            self.is_partial = method_type['partial']
            self.is_extern = method_type['extern']
            self.is_virtual = method_type['virtual']
            self.is_abstract = method_type['abstract']
        else:
            self.is_delegate = False
            self.is_partial = False
            self.is_extern = False
            self.is_virtual = False
            self.is_abstract = False
        self.pos = pos


class MethodInfo(ObjectInfo):
    def __init__(self, father, xml, method_str, properties=MethodProperties()):
        super().__init__(father, xml)
        self.data_type = []
        if properties:
            self.access_modifier = properties.access_modifier
            self.is_static = properties.is_static
            self.is_delegate = properties.is_delegate
            self.is_partial = properties.is_partial
            self.is_extern = properties.is_extern
            self.is_virtual = properties.is_virtual
            self.is_abstract = properties.is_abstract
        self.args = []
        self.is_override = False
        self.is_constructor = False
        self.is_destructor = False
        self.rest_of_string = []
        self.is_operator = False
        self.is_event = False
        self.is_async = False

        self._angle_brackets_count = 0
        self.parse_args = False

        self.get_method_info(method_str, properties.pos)

    def get_method_info(self, strings, pos):
        brackets = {
            '(': Bracket('(', ')'),
            '{': Bracket('{', '}'),
            '[': Bracket('[', ']'),
            '<': Bracket('<', '>'),
        }
        bracket = Bracket()
        arg = []
        for i in range(pos[0], len(strings)):
            j = pos[1] if pos[0] == i else 0
            start = j
            while j < len(strings[i]):
                if self.parse_args:
                    if bracket.count == 0:
                        if strings[i][j] in brackets:
                            bracket = brackets[strings[i][j]]
                            bracket.count += 1
                        if strings[i][j] == ')':
                            if start != j:
                                arg.append(strings[i][start:j])
                            if len(arg) != 0:
                                self.args.append(arg)

                            if strings[i][j + 1:] != '':
                                self.rest_of_string.append(strings[i][j + 1:])
                            self.rest_of_string.extend(strings[i + 1:])
                            return
                        if strings[i][j] == ',':
                            if start != j:
                                arg.append(strings[i][start:j])
                            if len(arg) != 0:
                                self.args.append(arg)
                            arg = []
                            start = j + 1
                    else:  # if inside brackets then just skip
                        bracket.count = parse_brackets(
                            bracket.opening,
                            bracket.closing,
                            strings[i][j],
                            bracket.count,
                        )
                else:
                    if strings[i][j] == ' ' or strings[i][j] == '(':
                        if start != j:
                            self.word_parser(strings[i][start:j].strip())
                        if strings[i][j] == '(':  # if char == ( then
                            if not self.name:     # starting to parse args
                                raise NotAMethodException
                            self.parse_args = True
                        start = j + 1
                j += 1

            if start != j:
                if self.parse_args:
                    arg.append(strings[i][start:j])
                else:
                    self.word_parser(strings[i][start:].strip())

    def word_parser(self, word):
        if word == 'throw':
            raise NotAMethodException
        elif word == 'new':
            return
        if (isinstance(self.father, ClassInfo) or
                isinstance(self.father, StructInfo)):
            if word == f'~{self.father.name}':
                self.name.append(word)
                self.is_destructor = True
                return
            elif word == self.father.name:
                self.name.append(word)
                self.is_constructor = True
                return
        if is_access_modifier(word):
            self.access_modifier = change_access_modifier(self.access_modifier,
                                                          word)
        elif word == 'static':
            self.is_static = True
        elif word == 'partial':
            self.is_partial = True
        elif word == 'abstract':
            self.is_abstract = True
        elif word == 'virtual':
            self.is_virtual = True
        elif word == 'extern':
            self.is_extern = True
        elif word == 'virtual':
            self.is_virtual = True
        elif word == 'override':
            self.is_override = True
        elif word == 'operator':
            self.is_operator = True
        elif word == 'event':
            self.is_event = True
        elif word == 'async':
            self.is_async = True
        elif word == 'new':
            return
        else:
            if self.is_operator and is_operator(word):
                self.name.append(word)
                return

            if len(self.name) == 0:
                pos, self._angle_brackets_count = data_type_parser(
                    word, self.data_type, self._angle_brackets_count
                )
                if pos > len(word) - 1:
                    return
                else:
                    if DATA_TYPE_REGEX1.match(word[pos:]):
                        self.name.append(word[pos:])
                    else:
                        raise WrongExpressionException
            else:
                if DATA_TYPE_REGEX2.match(word):
                    self.name.append(word)
                else:
                    raise WrongExpressionException
