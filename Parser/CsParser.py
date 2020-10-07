import os
import sys

from Parser.SemicolonParser import SemicolonParser
from Tools.Classes import Bracket
from Tools.Functions import parse_quotes, parse_brackets, is_field_checking
from Tools.Exceptions import (NotAMethodException,
                              NotAPropertyException,
                              NotAFieldException,
                              MissingBracketException,
                              WrongExpressionException)
from Tools import Regexes
import ProjectStructure as PS

ENUM_BRACKETS = {
    '{': Bracket('{', '}'),
    '[': Bracket('[', ']'),
    '<': Bracket('<', '>'),
    '(': Bracket('(', ')')
}


class StateArgs:
    def __init__(self, char, pos, line):
        self.char = char
        self.pos = pos
        self.line = line


class CsParser:
    def __init__(self):
        self.file_info = None
        self.curr_elem = None
        self.previous_pos = 0
        self.bracket = Bracket()
        self.enum_bracket = Bracket()
        self.previous_lines = []
        self.xml = []
        self.end_of_line = False
        self.line_number = 0
        self.current_state = self.default_state
        self.previous_state = None
        self.skip_text = False
        # self.encoding = None

    def parse(self, path, encodings):
        if sys.stdin and not path:
            buffer = sys.stdin.buffer.read()
            for encoding in encodings:
                try:
                    data = buffer.decode(encoding)
                    return self.parse_file_data('StdIn', data, is_std=True)
                except UnicodeDecodeError:
                    pass
            else:
                data = buffer.decode(encodings[0], errors='replace')
                return self.parse_file_data('StdIn', data, is_std=True)

        for encoding in encodings:
            try:
                with open(path, mode="r", encoding=encoding) as file:
                    return self.parse_file_data(path, file)
            except UnicodeDecodeError:
                pass
        else:
            with open(path, mode="r", encoding=encodings[0], errors='replace')\
                    as file:
                return self.parse_file_data(path, file)

    def parse_file_data(self, name, file, is_std=False):
        self.file_info = PS.FileInfo(os.path.basename(name))
        self.curr_elem = self.file_info

        if not is_std:
            line = file.readline()
            while line:
                self.parse_line(line)
                line = file.readline()
        else:
            lines = file.split('\n')
            for line in lines:
                self.parse_line(line)

        if self.bracket.count != 0:
            raise MissingBracketException()
        else:
            return self.file_info

    def parse_line(self, line):
        self.line_number += 1
        line = line.strip()
        if not line:
            return
        if line[0] == b'\xef\xbb\xbf'.decode('utf-8'):
            line = line[1:]
        if line[0] == '#':
            return
        # if line contains /// then it's xml
        if len(line) > 2 and line[:3] == '///':
            self.xml.append(line[3: len(line)])
        else:
            state_args = StateArgs('', 0, '')
            i = 0
            self.end_of_line = False
            while i < len(line):
                if line[i] == '/' and i != len(line)-1 and not self.skip_text:
                    # if line contains // then it's comment
                    if line[i+1] == '/':
                        self.parse_comment(line, i)
                        return
                    # if line contains /* then it's multi-line comment
                    if line[i+1] == '*':
                        self.parse_comment(line, i)
                        self.skip_text = True
                        self.previous_state = self.current_state
                        self.current_state = self.in_comment_state

                # if char == \" or \' then in we should skip all text
                # before next \" or \'
                elif line[i] == '\"' or line[i] == '\'':
                    i = parse_quotes(line[i], line, i + 1)
                    continue
                # if char == [ then it's an Attribute
                # I decided to skip them
                elif (
                        not self.skip_text and
                        line[i] == '[' and
                        not self.previous_lines and
                        Regexes.IS_ATTRIBUTE_REGEX.match(
                            line[self.previous_pos: i + 1]
                        )
                ):
                    self.bracket = Bracket('[', ']', 1)
                    self.previous_state = self.current_state
                    self.current_state = self.skip_text_state
                    self.skip_text = True
                    i += 1
                try:
                    state_args.char = line[i]
                    state_args.pos = i
                    state_args.line = line
                    self.current_state(state_args)
                except (NotAFieldException, NotAMethodException):
                    self.previous_lines = []
                    self.previous_pos = i + 1
                i += 1
            else:
                if (
                        self.previous_pos != len(line) and
                        not self.end_of_line and
                        not self.skip_text
                ):
                    self.previous_lines.append(
                        line[self.previous_pos:].strip()
                    )
                self.previous_pos = 0

    # Elements always end with ';' or '{'
    # If ';' then it may be a field, delegate or method without body
    # If '{' then it may be a class, enum, namespace, interface, struct,
    # method, property or it's an unfinished field
    def default_state(self, args):
        if args.char == ';':
            self.end_of_line_checking(args.pos, args.line)
            self.add_semicolon(
                SemicolonParser(
                    self.curr_elem, self.previous_lines, self.xml
                ).parse()
            )
            self.xml = []
            self.previous_lines = []
            self.previous_pos = args.pos + 1
        elif args.char == '{':
            self.end_of_line_checking(args.pos, args.line)
            self.previous_pos = args.pos + 1
            if is_field_checking(self.previous_lines):
                self.previous_lines.append('{')
                self.bracket.count += 1
                self.current_state = self.in_field_state
            else:
                self.parse_element()
                self.xml = []
                self.previous_lines = []
        elif args.char == '}':
            if self.curr_elem is not None:
                self.curr_elem = self.curr_elem.father
            else:
                raise MissingBracketException
            self.previous_pos = args.pos + 1

    # Skipping text until the elements body ends (bracket.count != 0)
    def skip_text_state(self, args):
        self.bracket.count = parse_brackets(
            self.bracket.opening,
            self.bracket.closing,
            args.char,
            self.bracket.count,
        )
        if self.bracket.count == 0:
            self.previous_pos = args.pos + 1
            self.current_state = self.previous_state
            self.skip_text = False

    # Skipping text until '*/'
    def in_comment_state(self, args):
        if (args.pos != len(args.line) - 1 and
                args.line[args.pos:args.pos+2] == '*/'):
            self.current_state = self.previous_state
            self.previous_pos = args.pos + 2
            self.skip_text = False

    # Field ends when we found ';'
    def in_field_state(self, args):
        if args.char == ';':
            self.previous_lines.append(
                args.line[self.previous_pos:args.pos + 1]
            )
        elif args.char == '{':
            self.previous_lines.append('{')
            self.bracket.count += 1
        elif args.char == '}':
            self.bracket.count -= 1
            self.previous_lines.append('}')
            if self.bracket.count == 0:
                self.current_state = self.default_state
        self.previous_pos = args.pos + 1

    def in_property_state(self, args):
        self.curr_elem.parse_property_body(args)
        if self.curr_elem.curly_brackets_count == 0:
            if (not self.curr_elem.has_get_value
                    and not self.curr_elem.has_set_value):
                raise WrongExpressionException
            self.curr_elem.father.add_property(self.curr_elem)
            self.bracket.count = 0
            self.previous_lines = []
            self.previous_pos = args.pos + 1
            self.current_state = self.default_state
            self.curr_elem = self.curr_elem.father

    # Enum items ends with ','
    def in_enum_state(self, args):
        if (args.char == '(' and self.enum_bracket.opening == ')' or
                args.char == '[' and self.enum_bracket.opening == ']' or
                args.char == '{' and self.enum_bracket.opening == '}' or
                args.char == '<' and self.enum_bracket.opening == '>'):
            self.bracket.count += 1
        elif (self.enum_bracket.count != 0 and
              (args.char == ')' and self.enum_bracket.opening == '(' or
               args.char == ']' and self.enum_bracket.opening == '[' or
               args.char == '}' and self.enum_bracket.opening == '{' or
               args.char == '>' and self.enum_bracket.opening == '<')):
            self.enum_bracket.count -= 1
        else:
            if args.char == ',':
                self.previous_lines.append(
                    args.line[self.previous_pos:args.pos]
                )
                self.curr_elem.add_enum_field(self.xml, self.previous_lines)
                self.previous_lines = []
                self.xml = []
                self.previous_pos = args.pos + 1
            elif args.char == '}':
                line = args.line[self.previous_pos:args.pos].strip()
                if line:
                    self.previous_lines.append(line)
                if self.previous_lines:
                    self.curr_elem.add_enum_field(
                        self.xml, self.previous_lines
                    )
                self.xml = []
                self.previous_lines = []
                self.previous_pos = args.pos + 1
                self.curr_elem = self.curr_elem.father
                self.current_state = self.default_state

    def parse_element(self):
        match = False
        t = None

        for line in self.previous_lines:
            if Regexes.IS_CLASS_REGEX.search(line):
                t = PS.ClassInfo(self.curr_elem, self.previous_lines, self.xml)
                self.curr_elem.add_class(t)
                match = True
            elif Regexes.IS_INTERFACE_REGEX.search(line):
                t = PS.InterfaceInfo(
                    self.curr_elem, self.previous_lines, self.xml
                )
                self.curr_elem.add_interface(t)
                match = True
            elif Regexes.IS_ENUM_REGEX.search(line):
                t = PS.EnumInfo(self.curr_elem, self.previous_lines, self.xml)
                self.curr_elem.add_enum(t)
                self.current_state = self.in_enum_state
                match = True
            elif Regexes.IS_NAMESPACE_REGEX.search(line):
                t = PS.NamespaceInfo(
                    self.curr_elem, self.previous_lines, self.xml
                )
                self.curr_elem.add_namespace(t)
                match = True
            elif Regexes.IS_EVENT_REGEX.search(line):
                self.curr_elem.add_event(
                    PS.EventInfo(self.curr_elem, self.previous_lines, self.xml)
                )
                self.bracket = Bracket('{', '}', 1)
                self.skip_text = True
                self.previous_state = self.current_state
                self.current_state = self.skip_text_state
                return
            elif Regexes.IS_STRUCT_REGEX.search(line):
                t = PS.StructInfo(
                    self.curr_elem, self.previous_lines, self.xml
                )
                self.curr_elem.add_struct(t)
                match = True
            if match:
                self.curr_elem = t
                break
        else:  # if none of the above then it's probably a Property
            if self.previous_lines[-1][-1] == ')':
                self.bracket = Bracket('{', '}', 1)
                self.skip_text = True
                self.previous_state = self.current_state
                self.current_state = self.skip_text_state
                try:
                    method = PS.MethodInfo(
                            self.curr_elem, self.previous_lines, self.xml
                        )
                    if method.is_constructor:
                        self.curr_elem.add_constructor(method)
                    else:
                        self.curr_elem.add_method(method)
                except NotAMethodException:  # If not a method then just skip
                    pass
                return

            self.bracket = Bracket('{', '}', 1)
            try:
                self.curr_elem = PS.PropertyInfo(
                    self.curr_elem, self.previous_lines, self.xml
                )
                self.current_state = self.in_property_state
            except NotAPropertyException:
                self.bracket = Bracket('{', '}', 1)
                self.skip_text = True
                self.previous_state = self.current_state
                self.current_state = self.skip_text_state

    def parse_comment(self, line, position):
        if position > 0:
            if self.previous_pos != position and not self.skip_text:
                self.previous_lines.append(
                    line[self.previous_pos: position].strip()
                )
            self.previous_pos = 0

    def end_of_line_checking(self, position, line):
        if (position != len(line) - 1 and  # If not end of line
                position != 0 and self.previous_pos != position):
            self.previous_lines.append(
                line[self.previous_pos:position].strip()
            )
            self.previous_pos = position
        elif position == len(line) - 1:  # If end of line
            if (self.previous_pos < len(line) - 1 and
                    self.previous_pos != position):
                self.previous_lines.append(line[self.previous_pos: -1].strip())
            self.end_of_line = True

    # Adding semicolon element to current father
    def add_semicolon(self, obj):
        if type(obj) == PS.EventInfo:
            self.curr_elem.add_event(obj)
        elif obj.is_delegate:
            self.curr_elem.add_delegate(obj)
        elif type(obj) == PS.FieldInfo:
            self.curr_elem.add_field(obj)
        elif type(obj) == PS.MethodInfo:
            self.curr_elem.add_method(obj)

    def __str__(self):
        return ''.join(str(self.curr_elem))
