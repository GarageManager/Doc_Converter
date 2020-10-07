from Tools.Exceptions import MissingQuoteException
from Tools.Regexes import IS_FIELD_REGEX, DATA_TYPE_REGEX1, DATA_TYPE_REGEX2
from Tools.Enums import AccessModifiers
from Tools.Classes import FuncArgs, TextParams
from Tools.Exceptions import WrongExpressionException

ACCESS_MODIFIERS_DICT = {
    "public": AccessModifiers.Public,
    "internal": AccessModifiers.Internal,
    "private": AccessModifiers.Private,
    "protected": AccessModifiers.Protected,
}

OPERATORS = ('!', '++', '--', '~', 'true', 'false', '+', '-', '*', '/', '%',
             '&', '|', '^', '<<', '>>', '==', '!=', '<', '>', '<=', '>=')


# Decorator for ProjectStructure classes
def parse_obj(func):
    def wrapper(*args):
        self_obj, strings, separators = args
        f_args = FuncArgs(strings)

        for f_args.str_num in range(len(strings)):
            start = 0
            f_args.pos = 0
            while f_args.pos < len(strings[f_args.str_num]):
                if strings[f_args.str_num][f_args.pos] in separators:
                    if start != f_args.pos:
                        self_obj.word_parser(
                            strings[f_args.str_num][start:f_args.pos].strip()
                        )
                        if func(self_obj, f_args):
                            return
                    start = f_args.pos + 1
                f_args.pos += 1
            if start != f_args.pos:
                self_obj.word_parser(
                    strings[f_args.str_num][start:f_args.pos].strip()
                )
                if func(self_obj, f_args):
                    return
    return wrapper


def parse_quotes(quote, string, position):
    slash_counter = 0
    for i in range(position, len(string)):
        if string[i] == "\\":
            slash_counter += 1
        else:
            if string[i] == quote:
                if slash_counter % 2 == 0:
                    return i + 1
            slash_counter = 0
    raise MissingQuoteException


def is_field_checking(strings):
    for string in strings:
        start = 0
        for i in range(len(string)):
            if string[i] == '(':
                return False
            elif string[i] == ' ':
                start = i + 1
            elif string[i] == '=':
                if i < len(string) - 1:
                    end = i + 2
                else:
                    end = i + 1

                if IS_FIELD_REGEX.search(string[start:end]):
                    return True
                return False


def parse_brackets(opening_bracket, closing_bracket, symbol, bracket_counter):
    if symbol == closing_bracket:
        return bracket_counter - 1
    if symbol == opening_bracket:
        return bracket_counter + 1
    return bracket_counter


def is_access_modifier(string):
    return string in ACCESS_MODIFIERS_DICT


def change_access_modifier(curr_acc_mod, string):
    acc_mod = ACCESS_MODIFIERS_DICT[string]

    if curr_acc_mod is AccessModifiers.Empty:
        curr_acc_mod = acc_mod
    elif (curr_acc_mod is AccessModifiers.Private and
          acc_mod is AccessModifiers.Protected):
        curr_acc_mod = AccessModifiers.PrivateProtected
    elif (
            curr_acc_mod is AccessModifiers.Protected and
            acc_mod is AccessModifiers.Internal
    ):
        curr_acc_mod = AccessModifiers.ProtectedInternal
    else:
        raise WrongExpressionException

    return curr_acc_mod


def access_modifier_to_string(modifier):
    if modifier == AccessModifiers.Protected:
        return 'protected '
    if modifier == AccessModifiers.Public:
        return 'public '
    if modifier == AccessModifiers.Private:
        return 'private '
    if modifier == AccessModifiers.PrivateProtected:
        return 'private protected '
    if modifier == AccessModifiers.ProtectedInternal:
        return 'protected internal '
    if modifier == AccessModifiers.Internal:
        return 'internal '


def data_type_parser(word, data_type_strings, brackets_count):
    previous_index = 0
    if (
            not data_type_strings and
            DATA_TYPE_REGEX1.match(word) or
            DATA_TYPE_REGEX2.match(word) and
            (brackets_count != 0 or data_type_strings and
             (word[0] == "." or
              data_type_strings[-1][-1] == "." or
              word[0] == "<" and
              data_type_strings[-1][-1] != ">"))
    ):
        for i in range(len(word)):
            if brackets_count != 0:
                brackets_count = parse_brackets("<", ">", word[i],
                                                brackets_count)
                if brackets_count == 0:
                    data_type_strings.append(word[previous_index: i + 1])
                    if i + 1 < len(word) and word[i + 1] == ".":
                        previous_index = i + 1
                    else:
                        return i + 1, brackets_count
            else:
                if word[i] == "<":
                    brackets_count += 1
        data_type_strings.append(word[previous_index:])
        return len(word), brackets_count
    return 0, brackets_count


def get_generic_info(obj):
    for j in range(len(obj.name[0])):
        if obj.name[0][j] == '<':
            new_name = obj.name[0][:j]
            if obj.name[0][j:]:
                obj.generic_info.append(obj.name[0][j:])
            obj.generic_info.extend(obj.name[1:])
            obj.name = new_name
            return
    if len(obj.name) > 1 and obj.name[1][0] == '<':
        new_name = obj.name[0]
        obj.generic_info = obj.name[1:]
        obj.name = new_name
        return
    obj.name = obj.name[0]


def is_operator(word):
    if word in OPERATORS:
        return True
    return False


def rgb_to_non_linear(red, green, blue):
    return f'{round(red / 255, 2)} {round(green / 255, 2)} ' \
           f'{round(blue / 255, 2)}'


def split_word_to_width(line_width, remaining_line_width, word, font, fpdf,
                        page_width):
    lines = []
    remaining_width = remaining_line_width
    prev_index = 0
    char_width = get_string_width('k', fpdf, page_width, font.name, font.size)
    curr_index = remaining_width // char_width
    if curr_index >= len(word) - 1:
        curr_index = len(word) // 2

    while curr_index < len(word) - 1:
        width = get_string_width(
            word[prev_index:curr_index], fpdf, page_width, font.name, font.size
        )
        if width >= remaining_width:
            for j in range(curr_index, prev_index, -1):
                width = get_string_width(
                    word[prev_index:j], fpdf, page_width, font.name, font.size
                )
                if width < remaining_width:
                    lines.append(
                        TextParams(word[prev_index:j], font, width=width)
                    )
                    prev_index = j
                    curr_index = min(
                        prev_index + line_width // char_width, len(word)
                    )
                    break
        else:
            width = get_string_width(
                word[prev_index:], fpdf, page_width, font.name, font.size
            )
            if width < remaining_width:
                lines.append(TextParams(word[prev_index:], font, width=width))
                prev_index = len(word)
                curr_index = len(word)
            else:
                for j in range(curr_index + 1, len(word)):
                    width = get_string_width(
                        word[prev_index:j+1], fpdf, page_width, font.name,
                        font.size
                    )
                    if width >= remaining_width:
                        lines.append(TextParams(
                            word[prev_index:j], font, width=width
                        ))
                        prev_index = j
                        curr_index = min(
                            prev_index + line_width // char_width,
                            len(word)
                        )
                        break
        remaining_width = line_width

    if prev_index != len(word):
        word = word[prev_index:]
        lines.append(
            TextParams(
                word,
                font,
                get_string_width(
                    word, fpdf, page_width, font.name, font.size
                )
            )
        )
    return lines


def escape(s):
    return s.replace('\\', '\\\\').replace(')', '\\)').replace('(', '\\(').\
        replace('\r', '\\r')


def format_data_type(data_type):
    if not data_type:
        return []

    res = []
    formatted_data = []
    for string in data_type:
        start_pos = 0
        for i in range(1, len(string)):
            if string[i] == ',':
                formatted_data.append(string[start_pos:i])
                formatted_data.append(', ')
                res.extend(formatted_data)
                start_pos = i + 1
                formatted_data = []
            elif not string[i].isspace() and string[i - 1].isspace():
                if string[start_pos:i].strip():
                    formatted_data.append(string[start_pos:i].strip())
                start_pos = i
        if string[start_pos:]:
            formatted_data.append(f'{string[start_pos:]} ')
    res.extend(formatted_data)
    return res


def format_argument(arg):
    data_type = []
    data_type.extend(arg[:-1])
    name = ''
    for i in range(len(arg[-1]) - 1, 0, -1):
        if arg[-1][i].isspace():
            name = arg[-1][i+1:]
            data_type.append(arg[-1][:i+1])
            break

    return format_data_type(data_type), name


def get_string_width(string, fpdf, page_width, font_name='', font_size=0):
    if font_name and font_size:
        fpdf.set_font(font_name, size=font_size)
    string_width = fpdf.get_string_width(string)
    multiplier = 2.9 - 2.9 * (string_width / (page_width * 10))
    return int(string_width * multiplier)
