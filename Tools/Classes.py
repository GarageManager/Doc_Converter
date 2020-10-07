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


class TextParams:
    def __init__(self, text, font, width=0, is_link=False, link=None):
        self.text = text
        self.font = font
        self.width = width
        self.is_link = is_link
        self.link = link


class Lines:
    def __init__(self):
        self.lines = []
        self.new_line = False

    def add_line(self, line):
        if not line:
            return
        if not self.lines or self.new_line:
            self.lines.append([line, ])
        else:
            self.lines[-1].append(line)

    def add_new_line(self, line):
        if not line:
            self.new_line = True
            return
        self.lines.append([line, ])


class Link:
    def __init__(self, page, pos_y):
        self.page = page
        self.pos_y = pos_y

    def __eq__(self, other):
        return self.page == other.page and self.pos_y == other.pos_y

    def __bool__(self):
        return self.page >= 0 and self.pos_y >= 0
