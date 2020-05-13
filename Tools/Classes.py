class StateArgs:
    def __init__(self, char, pos, line):
        self.char = char
        self.pos = pos
        self.line = line


class Bracket:
    def __init__(self, opening_bracket="", closing_bracket="", count=0):
        self.opening = opening_bracket
        self.closing = closing_bracket
        self.count = count


class FuncArgs:
    def __init__(self, strings, str_num=0, pos=0):
        self.strings = strings
        self.str_num = str_num
        self.pos = pos
