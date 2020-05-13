import unittest

from Parser.SemicolonParser import SemicolonParser
import ProjectStructure as PS
from Tools import (Exceptions as E, Functions as F)


class TestSemicolonParser(unittest.TestCase):
    def test_delegate(self):
        strings = ['public ', 'delegate ', 'void a(int w)']
        r = SemicolonParser(PS.FileInfo('c'), strings, None).parse()
        self.assertEqual(type(r), PS.MethodInfo)
        self.assertEqual(r.data_type, ['void'])
        self.assertEqual(r.args, [['int w']])
        self.assertEqual(r.is_delegate, True)
        self.assertEqual(r.name, ['a'])

    def test_func(self):
        strings = ['private protected Func<int', ', int>', 'func']
        r = SemicolonParser(PS.FileInfo('c'), strings, None).parse()
        self.assertEqual(type(r), PS.FieldInfo)
        self.assertEqual(r.access_modifier, F.AccessModifiers.PrivateProtected)
        self.assertEqual(r.data_type, ['Func<int', ',', 'int>'])
        self.assertEqual(r.is_delegate, True)
        self.assertEqual(r.name, 'func')

    def test_partial(self):
        strings = ['public static partial void part(int[] a,S<int, int> b)']
        r = SemicolonParser(PS.FileInfo('c'), strings, None).parse()
        self.assertEqual(type(r), PS.MethodInfo)
        self.assertEqual(r.access_modifier, F.AccessModifiers.Public)
        self.assertEqual(r.is_static, True)
        self.assertEqual(r.args, [['int[] a'], ['S<int, int> b']])
        self.assertEqual(r.data_type, ['void'])
        self.assertEqual(r.name, ['part'])

    def test_abstract(self):
        strings = ['internal', 'abstract', 'string', 'abst(', 'int[]',
                   'a', ',', 'S', '<', 'int', ',', 'int', '>', 'b', ')']
        r = SemicolonParser(PS.FileInfo('c'), strings, None).parse()
        self.assertEqual(type(r), PS.MethodInfo)
        self.assertEqual(r.access_modifier, F.AccessModifiers.Internal)
        self.assertEqual(
            r.args, [['int[]', 'a'], ['S', '<', 'int', ',', 'int', '>', 'b']]
        )
        self.assertEqual(r.data_type, ['string'])
        self.assertEqual(r.name, ['abst'])

    def test_extern(self):
        strings = ['protected internal extern Dict<int, int> ex()']
        r = SemicolonParser(PS.FileInfo('c'), strings, None).parse()
        self.assertEqual(type(r), PS.MethodInfo)
        self.assertEqual(
            r.access_modifier, F.AccessModifiers.ProtectedInternal
        )
        self.assertEqual(r.args, [])
        self.assertEqual(r.data_type, ['Dict<int,', 'int>'])
        self.assertEqual(r.name, ['ex'])

    def test_virtual(self):
        strings = ['virtual int virt()']
        r = SemicolonParser(PS.FileInfo('c'), strings, None).parse()
        self.assertEqual(type(r), PS.MethodInfo)
        self.assertEqual(r.access_modifier, F.AccessModifiers.Empty)
        self.assertEqual(r.args, [])
        self.assertEqual(r.data_type, ['int'])
        self.assertEqual(r.name, ['virt'])

    def test_field1(self):
        strings = ['example<int>', '.', 'subclass<int> asihfb']
        r = SemicolonParser(PS.FileInfo('c'), strings, None).parse()
        self.assertEqual(type(r), PS.FieldInfo)
        self.assertEqual(r.is_delegate, False)
        self.assertEqual(r.value, [])
        self.assertEqual(r.data_type, ['example<int>', '.', 'subclass<int>'])
        self.assertEqual(r.name, 'asihfb')

    def test_field2(self):
        strings = ['example<int>', '.', 'subclass<int> asihfb = '
                                        'new example<int>.subclass<int>()']
        r = SemicolonParser(PS.FileInfo('c'), strings, None).parse()
        self.assertEqual(type(r), PS.FieldInfo)
        self.assertEqual(r.is_delegate, False)
        self.assertEqual(r.value, [' = new example<int>.subclass<int>()'])
        self.assertEqual(r.data_type, ['example<int>', '.', 'subclass<int>'])
        self.assertEqual(r.name, 'asihfb')

    def test_incorrect1(self):
        strings = ['protected internal Dict<int, int> ex()']
        exc = None
        try:
            _ = SemicolonParser(PS.FileInfo('c'), strings, None).parse()
        except E.ParseException as e:
            exc = e
        self.assertEqual(type(exc), E.NotAFieldException)

    def test_incorrect2(self):
        strings = ['protected internal partial Dict<int, int> e!x()']
        exc = None
        try:
            _ = SemicolonParser(PS.FileInfo('c'), strings, None).parse()
        except E.ParseException as e:
            exc = e
        self.assertEqual(type(exc), E.WrongExpressionException)

    def test_incorrect3(self):
        strings = ['a = a() + b{}']
        exc = None
        try:
            _ = SemicolonParser(PS.FileInfo('c'), strings, None).parse()
        except E.ParseException as e:
            exc = e
        self.assertEqual(type(exc), E.NotAFieldException)

    def test_incorrect4(self):
        strings = ['protected public internal partial Dict<int, int> ex()']
        exc = None
        try:
            _ = SemicolonParser(PS.FileInfo('c'), strings, None).parse()
        except E.ParseException as e:
            exc = e
        self.assertEqual(type(exc), E.WrongExpressionException)


class TestFunctions(unittest.TestCase):
    def test_quotes1(self):
        string = '\\"\\"third"'
        self.assertEqual(len(string), F.parse_quotes('"', string, 0))

    def test_quotes2(self):
        string = '\\\\\\"\\"third"'
        self.assertEqual(len(string), F.parse_quotes('"', string, 0))

    def test_quotes3(self):
        string = '\\\\\\"\\"third" + 1'
        self.assertEqual(len(string) - 4, F.parse_quotes('"', string, 0))

    def test_quotes_incorrect1(self):
        string = 'word, word'
        exc = None
        try:
            F.parse_quotes('"', string, 0)
        except E.ParseException as e:
            exc = e
        self.assertEqual(E.MissingQuoteException, type(exc))

    def test_quotes_incorrect2(self):
        string = 'word\\", word'
        exc = None
        try:
            F.parse_quotes('"', string, 0)
        except E.ParseException as e:
            exc = e
        self.assertEqual(E.MissingQuoteException, type(exc))

    def test_parse_bracket(self):
        opening = '('
        closing = ')'
        count = 1

        char1 = '('
        char2 = 's'
        char3 = ')'

        count = F.parse_brackets(opening, closing, char1, count)
        self.assertEqual(2, count)
        count = F.parse_brackets(opening, closing, char2, count)
        self.assertEqual(2, count)
        count = F.parse_brackets(opening, closing, char3, count)
        self.assertEqual(1, count)

    def test_is_operator(self):
        char = '+'
        self.assertEqual(True, F.is_operator(char))
        char = '~'
        self.assertEqual(True, F.is_operator(char))
        char = 'a'
        self.assertEqual(False, F.is_operator(char))
        char = 'operator'
        self.assertEqual(False, F.is_operator(char))
        char = '<<'
        self.assertEqual(True, F.is_operator(char))
        char = '!='
        self.assertEqual(True, F.is_operator(char))
        char = '-%'
        self.assertEqual(False, F.is_operator(char))

    def test_is_field(self):
        strings = ['public readonly Dict<int, int> a = new Dict<int, int>']
        self.assertEqual(True, F.is_field_checking(strings))
        strings = ['void a(string s = "=", string s1 = "{}=;")']
        self.assertEqual(False, F.is_field_checking(strings))
        strings = ['void a(bool b = 2 <= 4']
        self.assertEqual(False, F.is_field_checking(strings))


if __name__ == "__main__":
    unittest.main()
