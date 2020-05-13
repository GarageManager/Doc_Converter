from Tools.Exceptions import MissingQuoteException
from Tools.Regexes import IS_FIELD_REGEX, DATA_TYPE_REGEX1, DATA_TYPE_REGEX2
from Tools.Enums import AccessModifiers
from Tools.Classes import FuncArgs
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


def data_type_parser(word, data_type_string, brackets_count):
    previous_index = 0
    if (
            not data_type_string and
            DATA_TYPE_REGEX1.match(word) or
            DATA_TYPE_REGEX2.match(word) and
            (brackets_count != 0 or data_type_string and
             (word[0] == "." or
              data_type_string[-1][-1] == "." or
              word[0] == "<" and
              data_type_string[-1][-1] != ">"))
    ):
        for i in range(len(word)):
            if brackets_count != 0:
                brackets_count = parse_brackets("<", ">", word[i],
                                                brackets_count)
                if brackets_count == 0:
                    data_type_string.append(word[previous_index: i + 1])
                    if i + 1 < len(word) and word[i + 1] == ".":
                        previous_index = i + 1
                    else:
                        return i + 1, brackets_count
            else:
                if word[i] == "<":
                    brackets_count += 1
        data_type_string.append(word[previous_index:])
        return len(word), brackets_count
    return 0, brackets_count


def get_generic_info(obj):
    for j in range(len(obj.name[0])):
        if obj.name[0][j] == '<':
            new_name = obj.name[0][:j]
            if obj.name[0][j:]:
                obj.generic_info.append(obj.name[0][j:])
            obj.generic_info.extend(obj.name[0+1:])
            obj.name = new_name
            return
    obj.name = obj.name[0]


def is_operator(word):
    if word in OPERATORS:
        return True
    return False
