from Parser.SemicolonParser import SemicolonParser
from Tools.Classes import Bracket, StateArgs
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


def parse(path, encoding, std=None):
    parser = Parser()
    if std and not path:
        return parser.parse_data('None', std)
    with open(path, mode="r", errors='replace',
              encoding=encoding) as file:
        return parser.parse_data(path, file)


class Parser:
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
        self.skip_text = False

    def parse_data(self, name, file):
        self.file_info = PS.FileInfo(name)
        self.curr_elem = self.file_info
        line = file.readline()

        if line[0] == b'\xef\xbb\xbf'.decode('utf-8'):
            line = line[1:]

        while line:
            self.parse_line(line)
            line = file.readline()

        if self.bracket.count != 0:
            raise MissingBracketException()
        else:
            return [self.file_info, ]

    def parse_line(self, line):
        self.line_number += 1
        line = line.strip()
        if not line:
            return
        if line[0] == '#':
            return
        # if line contains /// then it's xml
        if len(line) > 2 and line[:3] == '///':
            self.xml.append(line[3: len(line)])
        else:
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
                    self.current_state = self.skip_text_state
                    self.skip_text = True
                    i += 1
                try:
                    self.current_state(StateArgs(line[i], i, line))
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
    # If ';' then it may be field, delegate or method without body
    # If { then it may be class, enum, namespace, interface, struct, method,
    # property or it's an unfinished field
    def default_state(self, args):
        if args.char == ';':
            self.end_of_line_checking(args.pos, args.line)
            self.add_semicolon(
                SemicolonParser(
                    self.curr_elem, self.previous_lines, self.xml
                ).parse()
            )
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
                self.parse_element(self.xml)
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
            if type(self.curr_elem) == PS.EnumInfo:
                self.current_state = self.in_enum_state
            else:
                self.current_state = self.default_state
            self.skip_text = False

    # Skipping text until '*/'
    def in_comment_state(self, args):
        if (args.pos != len(args.line) - 1 and
                args.line[args.pos:args.pos+2] == '*/'):
            self.current_state = self.default_state
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

    def property_begin_state(self, args):
        get_match = Regexes.GET_REGEX.search(args.line[args.pos:])
        set_match = Regexes.SET_REGEX.search(args.line[args.pos:])

        if get_match or set_match:
            self.curr_elem.get_set_flag = True
            self.previous_pos = args.pos
            if (not get_match or
                    set_match and set_match.start() < get_match.start()):
                self.current_state = self.property_set_state
                self.previous_pos += set_match.end()
            elif (not set_match or
                  get_match and get_match.start() < set_match.start()):
                self.current_state = self.property_get_state
                self.previous_pos += get_match.end()
        else:
            raise WrongExpressionException

    def property_get_state(self, args):
        if args.pos < self.previous_pos:
            return
        if args.char == '{':
            self.bracket.count += 1
        elif args.char == '}':
            self.bracket.count -= 1
            if self.bracket.count == 0:
                if args.line[self.previous_pos:args.pos]:
                    self.previous_lines.append(
                        args.line[self.previous_pos:args.pos]
                    )
                self.curr_elem.add_get_value(self.previous_lines)
                self.property_to_default(args.pos)
        else:
            self.parse_property_body(args, 's')

    def property_set_state(self, args):
        if args.pos < self.previous_pos:
            return
        if args.char == '{':
            self.bracket.count += 1
        elif args.char == '}':
            self.bracket.count -= 1
            if self.bracket.count == 0:
                if args.line[self.previous_pos:args.pos]:
                    self.previous_lines.append(
                        args.line[self.previous_pos:args.pos]
                    )
                self.curr_elem.add_set_value(self.previous_lines)
                self.property_to_default(args.pos)
        else:
            self.parse_property_body(args, 'g')

    def property_full_state(self, args):
        if args.pos < self.previous_pos:
            return
        if args.char == '{':
            self.bracket.count += 1
        elif args.char == '}':
            self.bracket.count -= 1
            if self.bracket.count == 0:
                if args.line[self.previous_pos:args.pos]:
                    self.previous_lines.append(
                        args.line[self.previous_pos:args.pos]
                    )
                self.curr_elem.add_value(self.previous_lines)
                self.property_to_default(args.pos)

    def parse_property_body(self, args, g_or_s):
        if self.bracket.count == 1:
            if (args.char == ' ' or
                    args.char == ';' or
                    args.pos == len(args.line) - 1):
                self.curr_elem.get_set_flag = True
            elif (
                    self.curr_elem.get_set_flag and
                    args.char == g_or_s and
                    len(args.line) - args.pos > 2 and
                    args.line[args.pos + 1] == 'e' and
                    args.line[args.pos + 2] == 't' and
                    (len(args.line) - 3 == args.pos or
                     args.line[args.pos + 3] == '{' or
                     args.line[args.pos + 3] == ' ' or
                     args.line[args.pos + 3] == ';')
            ):
                if args.line[self.previous_pos:args.pos]:
                    self.previous_lines.append(
                        args.line[self.previous_pos:args.pos]
                    )
                if args.char == 'g':
                    self.curr_elem.add_set_value(self.previous_lines)
                else:
                    self.curr_elem.add_get_value(self.previous_lines)
                self.previous_lines = []
                self.previous_pos = args.pos + 3
                self.current_state = self.property_full_state
            else:
                self.curr_elem.get_set_flag = False

    def property_to_default(self, pos):
        self.previous_lines = []
        self.previous_pos = pos + 1
        self.current_state = self.default_state
        self.curr_elem.father.add_property(self.curr_elem)
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
                self.curr_elem.add_enum_field(list(self.previous_lines))
                self.previous_lines = []
                self.previous_pos = args.pos + 1
            elif args.char == '}':
                line = args.line[self.previous_pos:args.pos].strip()
                if line:
                    self.previous_lines.append(line)
                if self.previous_lines:
                    self.curr_elem.add_enum_field(self.previous_lines)
                self.previous_lines = []
                self.previous_pos = args.pos + 1
                self.curr_elem = self.curr_elem.father
                self.current_state = self.default_state

    def parse_element(self, xml):
        match = False
        t = None

        for line in self.previous_lines:
            if Regexes.IS_CLASS_REGEX.search(line):
                t = PS.ClassInfo(self.curr_elem, self.previous_lines, xml)
                self.curr_elem.add_class(t)
                match = True
            elif Regexes.IS_INTERFACE_REGEX.search(line):
                t = PS.InterfaceInfo(self.curr_elem, self.previous_lines, xml)
                self.curr_elem.add_interface(t)
                match = True
            elif Regexes.IS_ENUM_REGEX.search(line):
                t = PS.EnumInfo(self.curr_elem, self.previous_lines, xml)
                self.curr_elem.add_enum(t)
                self.current_state = self.in_enum_state
                match = True
            elif Regexes.IS_NAMESPACE_REGEX.search(line):
                t = PS.NamespaceInfo(self.curr_elem, self.previous_lines, xml)
                self.curr_elem.add_namespace(t)
                match = True
            elif Regexes.IS_EVENT_REGEX.search(line):
                self.curr_elem.add_event(
                    PS.EventInfo(self.curr_elem, self.previous_lines, xml)
                )
                self.bracket = Bracket('{', '}', 1)
                self.skip_text = True
                self.current_state = self.skip_text_state
                return
            elif Regexes.IS_STRUCT_REGEX.search(line):
                t = PS.StructInfo(self.curr_elem, self.previous_lines, xml)
                self.curr_elem.add_struct(t)
                match = True
            if match:
                self.curr_elem = t
                break
        else:  # if none of the above then it's probably a Property
            if self.previous_lines[-1][-1] == ')':
                self.bracket = Bracket('{', '}', 1)
                self.skip_text = True
                self.current_state = self.skip_text_state
                try:
                    self.curr_elem.add_method(
                        PS.MethodInfo(self.curr_elem, self.previous_lines, xml)
                    )
                except NotAMethodException:  # If not a method then just skip
                    pass
                return

            self.bracket = Bracket('{', '}', 1)
            try:
                self.curr_elem = PS.PropertyInfo(
                    self.curr_elem, self.previous_lines, self.xml
                )
                self.current_state = self.property_begin_state
            except NotAPropertyException:
                self.bracket = Bracket('{', '}', 1)
                self.skip_text = True
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
                position != 0 and
                self.previous_pos != position):
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
