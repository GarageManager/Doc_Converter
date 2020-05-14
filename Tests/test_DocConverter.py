import unittest

import Parser
import ProjectStructure as PS
from Tools import (Exceptions as E, Functions as F)


class TestParseClass(unittest.TestCase):
    def test_simple_class(self):
        parser = Parser.Parser()
        parser.curr_elem = PS.FileInfo('c')
        string = 'public static class A {'
        parser.parse_line(string)
        res = parser.curr_elem
        self.assertEqual(type(res), PS.ClassInfo)
        self.assertEqual(res.is_static, True)
        self.assertEqual(res.access_modifier, F.AccessModifiers.Public)
        self.assertEqual(res.name, 'A')

    def test_generic_class(self):
        parser = Parser.Parser()
        parser.curr_elem = PS.FileInfo('c')
        strings = ['class SpecialNodeItem< T >: NodeItem < T > where',
                   'T: System.IComparable < T > {']
        for string in strings:
            parser.parse_line(string)
        res = parser.curr_elem
        self.assertEqual(type(res), PS.ClassInfo)
        self.assertEqual(res.access_modifier, F.AccessModifiers.Empty)
        self.assertEqual(res.name, 'SpecialNodeItem')
        self.assertEqual(res.generic_info, ['<', 'T', '>'])

    def test_abstract_class(self):
        parser = Parser.Parser()
        parser.curr_elem = PS.FileInfo('c')
        strings = ['private protected',
                   'abstract',
                   'class Aa<T, W>{']
        for string in strings:
            parser.parse_line(string)
        res = parser.curr_elem
        self.assertEqual(type(res), PS.ClassInfo)
        self.assertEqual(
            res.access_modifier, F.AccessModifiers.PrivateProtected
        )
        self.assertEqual(res.is_abstract, True)
        self.assertEqual(res.name, 'Aa')
        self.assertEqual(res.generic_info, ['<T,', 'W>'])

    def test_partial_class(self):
        parser = Parser.Parser()
        parser.curr_elem = PS.FileInfo('c')
        strings = ['partial', 'class', 'Aa', '<', 'T', ',', ' W', '>', '{']
        for string in strings:
            parser.parse_line(string)
        res = parser.curr_elem
        self.assertEqual(type(res), PS.ClassInfo)
        self.assertEqual(res.is_partial, True)
        self.assertEqual(res.name, 'Aa')
        self.assertEqual(res.generic_info, ['<', 'T', ',', 'W', '>'])

    def test_sealed_class(self):
        parser = Parser.Parser()
        parser.curr_elem = PS.FileInfo('c')
        strings = ['sealed', 'class', 'Aa', '{']
        for string in strings:
            parser.parse_line(string)
        res = parser.curr_elem
        self.assertEqual(type(res), PS.ClassInfo)
        self.assertEqual(res.is_sealed, True)
        self.assertEqual(res.name, 'Aa')
        self.assertEqual(res.generic_info, [])

    def test_invalid_class(self):
        parser = Parser.Parser()
        parser.curr_elem = PS.FileInfo('c')
        strings = ['public', 'inavlid', 'class', '{']
        res = None
        try:
            for string in strings:
                parser.parse_line(string)
        except E.WrongExpressionException as e:
            res = type(e)
        self.assertEqual(res, E.WrongExpressionException)


class TestParseInterface(unittest.TestCase):
    def test_simple_interface(self):
        parser = Parser.Parser()
        parser.curr_elem = PS.FileInfo('c')
        strings = ['public', 'interface', 'I', '{']
        for string in strings:
            parser.parse_line(string)
        res = parser.curr_elem
        self.assertEqual(type(res), PS.InterfaceInfo)
        self.assertEqual(res.access_modifier, F.AccessModifiers.Public)
        self.assertEqual(res.name, 'I')

    def test_inherited_interface(self):
        parser = Parser.Parser()
        parser.curr_elem = PS.FileInfo('c')
        strings = ['private protected interface II :'
                   ' System.Collections.IEnumerable{']
        for string in strings:
            parser.parse_line(string)
        res = parser.curr_elem
        self.assertEqual(type(res), PS.InterfaceInfo)
        self.assertEqual(res.name, 'II')
        self.assertEqual(not res.rest_of_string, False)
        self.assertEqual(
            res.access_modifier,
            F.AccessModifiers.PrivateProtected
        )


class TestParseEnum(unittest.TestCase):
    def test_simple_enum(self):
        parser = Parser.Parser()
        parser.curr_elem = PS.FileInfo('c')
        strings = ['private protected static enum e {one, two,',
                   '[something]', ' three}']
        for string in strings:
            parser.parse_line(string)
        res = parser.curr_elem.enums.pop()
        self.assertEqual(type(res), PS.EnumInfo)
        self.assertEqual(res.name, 'e')
        self.assertEqual(len(res.enum_fields), 3)

    def test_inherited_enum(self):
        parser = Parser.Parser()
        parser.curr_elem = PS.FileInfo('c')
        strings = [
            'enum',
            'Color: long',
            '{',
            'Red,',
            'Green,',
            'Blue',
            '}'
        ]
        for string in strings:
            parser.parse_line(string)
        res = parser.curr_elem.enums.pop()
        self.assertEqual(type(res), PS.EnumInfo)
        self.assertEqual(res.name, 'Color')
        self.assertEqual(res.rest_of_string, ['long'])
        self.assertEqual(len(res.enum_fields), 3)

    def test_invalid_enum1(self):
        parser = Parser.Parser()
        parser.curr_elem = PS.FileInfo('c')
        strings = ['public', 'inavlid', 'enum', '{']
        res = None
        try:
            for string in strings:
                parser.parse_line(string)
        except E.WrongExpressionException as e:
            res = type(e)
        self.assertEqual(res, E.WrongExpressionException)

    def test_invalid_enum2(self):
        parser = Parser.Parser()
        parser.curr_elem = PS.FileInfo('c')
        strings = ['public', 'enum', '1nvalid', '{']
        res = None
        try:
            for string in strings:
                parser.parse_line(string)
        except E.WrongExpressionException as e:
            res = type(e)
        self.assertEqual(res, E.WrongExpressionException)


class TestParseStruct(unittest.TestCase):
    def test_simple_struct(self):
        parser = Parser.Parser()
        parser.curr_elem = PS.FileInfo('c')
        string = 'static const struct d {'
        parser.parse_line(string)
        res = parser.curr_elem
        self.assertEqual(type(res), PS.StructInfo)
        self.assertEqual(res.name, 'd')
        self.assertEqual(res.rest_of_string, [])
        self.assertEqual(res.is_const, True)
        self.assertEqual(res.is_static, True)
        self.assertEqual(res.access_modifier, F.AccessModifiers.Empty)

    def test_inherited_strict(self):
        parser = Parser.Parser()
        parser.curr_elem = PS.FileInfo('c')
        string = 'protected readonly struct inh :Frrr{'
        parser.parse_line(string)
        res = parser.curr_elem
        self.assertEqual(type(res), PS.StructInfo)
        self.assertEqual(res.name, 'inh')
        self.assertEqual(res.is_readonly, True)
        self.assertEqual(res.rest_of_string, ['Frrr'])
        self.assertEqual(res.access_modifier, F.AccessModifiers.Protected)

    def test_invalid_struct1(self):
        parser = Parser.Parser()
        parser.curr_elem = PS.FileInfo('c')
        strings = ['public', 'invalid', 'struct', '{']
        res = None
        try:
            for string in strings:
                parser.parse_line(string)
        except E.WrongExpressionException as e:
            res = type(e)
        self.assertEqual(res, E.WrongExpressionException)

    def test_invalid_struct2(self):
        parser = Parser.Parser()
        parser.curr_elem = PS.FileInfo('c')
        strings = ['public', 'struct', '1nvalid', '{']
        res = None
        try:
            for string in strings:
                parser.parse_line(string)
        except E.WrongExpressionException as e:
            res = type(e)
        self.assertEqual(res, E.WrongExpressionException)


class TestParseNamespace(unittest.TestCase):
    def test_namespace(self):
        parser = Parser.Parser()
        parser.curr_elem = PS.FileInfo('c')
        strings = ['namespace', 'name1.name2', '.name3', '{']
        for string in strings:
            parser.parse_line(string)
        res = parser.curr_elem
        self.assertEqual(type(res), PS.NamespaceInfo)
        self.assertEqual(res.name, ['name1.name2', '.name3'])

    def test_invalid_namespace1(self):
        parser = Parser.Parser()
        parser.curr_elem = PS.FileInfo('c')
        strings = ['name1.name2', '.name3', 'namespace', '{']
        res = None
        try:
            for string in strings:
                parser.parse_line(string)
        except E.WrongExpressionException as e:
            res = type(e)
        self.assertEqual(res, E.WrongExpressionException)

    def test_invalid_namespace2(self):
        parser = Parser.Parser()
        parser.curr_elem = PS.FileInfo('c')
        strings = ['namespace', '.name3', '{']
        res = None
        try:
            for string in strings:
                parser.parse_line(string)
        except E.WrongExpressionException as e:
            res = type(e)
        self.assertEqual(res, E.WrongExpressionException)

    def test_invalid_namespace3(self):
        parser = Parser.Parser()
        parser.curr_elem = PS.FileInfo('c')
        strings = ['namespace', 'n.', '3name3', '{']
        res = None
        try:
            for string in strings:
                parser.parse_line(string)
        except E.WrongExpressionException as e:
            res = type(e)
        self.assertEqual(res, E.WrongExpressionException)


class TestParseProperty(unittest.TestCase):
    def test_set(self):
        parser = Parser.Parser()
        parser.curr_elem = PS.ClassInfo(None, 'class test')
        string = 'object test { set{ tmp = value;} }'
        parser.parse_line(string)
        res = parser.curr_elem.properties.pop()
        self.assertEqual(type(res), PS.PropertyInfo)
        self.assertEqual(res.name, ['test'])
        self.assertEqual(res.set_value, ['{ tmp = value;} '])
        self.assertEqual(res.data_type, ['object'])

    def test_get(self):
        parser = Parser.Parser()
        parser.curr_elem = PS.ClassInfo(None, 'class test')
        string = 'private static object test { get;}'
        parser.parse_line(string)
        res = parser.curr_elem.properties.pop()
        self.assertEqual(type(res), PS.PropertyInfo)
        self.assertEqual(res.name, ['test'])
        self.assertEqual(res.get_value, [';'])
        self.assertEqual(res.data_type, ['object'])

    def test_get_set(self):
        parser = Parser.Parser()
        parser.curr_elem = PS.ClassInfo(None, 'class test')
        strings = ['Property', 'property', '{', 'get', 'return', 'get', ';',
                   'set', 's', '=', 'value', ';', '}']
        for string in strings:
            parser.parse_line(string)
        res = parser.curr_elem.properties.pop()
        self.assertEqual(type(res), PS.PropertyInfo)
        self.assertEqual(res.name, ['property'])
        self.assertEqual(res.get_value, ['return', 'get', ';'])
        self.assertEqual(res.set_value, ['s', '=', 'value', ';'])
        self.assertEqual(res.data_type, ['Property'])

    def test_set_get(self):
        parser = Parser.Parser()
        parser.curr_elem = PS.ClassInfo(None, 'class test')
        string = 'Property property{set s=value;get return get;}'
        parser.parse_line(string)
        res = parser.curr_elem.properties.pop()
        self.assertEqual(type(res), PS.PropertyInfo)
        self.assertEqual(res.name, ['property'])
        self.assertEqual(res.get_value, [' return get;'])
        self.assertEqual(res.set_value, [' s=value;'])
        self.assertEqual(res.data_type, ['Property'])

    def test_empty_body(self):
        parser = Parser.Parser()
        parser.curr_elem = PS.ClassInfo(None, 'class test')
        string = 'Property empty{}'
        res = None
        try:
            parser.parse_line(string)
        except E.WrongExpressionException as e:
            res = type(e)
        self.assertEqual(res, E.WrongExpressionException)

    def test_indexer(self):
        parser = Parser.Parser()
        parser.curr_elem = PS.ClassInfo(None, 'class test')

        strings = ['public T this[int i]',
                   '{get { return arr[i]; }',
                   'set { arr[i] = value; } }']
        for string in strings:
            parser.parse_line(string)
        res = parser.curr_elem.properties.pop()

        self.assertEqual(type(res), PS.PropertyInfo)
        self.assertEqual(res.name, ['this[int', 'i]'])
        self.assertEqual(res.get_value, ['{ return arr[i]; }'])
        self.assertEqual(res.set_value, [' { arr[i] = value; } '])
        self.assertEqual(res.data_type, ['T'])


class TestParseMethod(unittest.TestCase):
    def test_simple(self):
        strings = ['public ', 'int ', ' a(int w) { return w };']
        parser = Parser.Parser()
        parser.curr_elem = PS.ClassInfo(None, 'class test')
        for string in strings:
            parser.parse_line(string)
        res = parser.curr_elem.methods.pop()
        self.assertEqual(type(res), PS.MethodInfo)
        self.assertEqual(res.name, ['a'])
        self.assertEqual(res.args, [['int w']])


class TestEvent(unittest.TestCase):
    def test_event1(self):
        strings = ['public static event EventHandler event1;']
        parser = Parser.Parser()
        parser.curr_elem = PS.ClassInfo(None, 'class test')
        for string in strings:
            parser.parse_line(string)
        res = parser.curr_elem.events.pop()

        self.assertEqual(type(res), PS.EventInfo)
        self.assertEqual(res.name, ['event1'])
        self.assertEqual(res.is_static, True)

    def test_event2(self):
        strings = ['event EventHandler event2 {add(); remove();}']
        parser = Parser.Parser()
        parser.curr_elem = PS.ClassInfo(None, 'class test')
        for string in strings:
            parser.parse_line(string)
        res = parser.curr_elem.events.pop()

        self.assertEqual(type(res), PS.EventInfo)
        self.assertEqual(res.name, ['event2'])
        self.assertEqual(res.is_static, False)


class TestSemicolonParser(unittest.TestCase):
    def test_delegate(self):
        strings = ['public ', 'delegate ', 'void a(int w);']
        parser = Parser.Parser()
        parser.curr_elem = PS.ClassInfo(None, 'class test')
        for string in strings:
            parser.parse_line(string)
        res = parser.curr_elem.delegates.pop()
        self.assertEqual(type(res), PS.MethodInfo)
        self.assertEqual(res.data_type, ['void'])
        self.assertEqual(res.args, [['int w']])
        self.assertEqual(res.is_delegate, True)
        self.assertEqual(res.name, ['a'])

    def test_func(self):
        strings = ['private protected Func<int', ', int>', 'func;']
        parser = Parser.Parser()
        parser.curr_elem = PS.ClassInfo(None, 'class test')
        for string in strings:
            parser.parse_line(string)
        res = parser.curr_elem.delegates.pop()
        self.assertEqual(type(res), PS.FieldInfo)
        self.assertEqual(
            res.access_modifier, F.AccessModifiers.PrivateProtected
        )
        self.assertEqual(res.data_type, ['Func<int', ',', 'int>'])
        self.assertEqual(res.is_delegate, True)
        self.assertEqual(res.name, 'func')

    def test_partial(self):
        strings = ['public static partial void part(int[] a,S<int, int> b);']
        parser = Parser.Parser()
        parser.curr_elem = PS.ClassInfo(None, 'class test')
        for string in strings:
            parser.parse_line(string)
        res = parser.curr_elem.methods.pop()
        self.assertEqual(type(res), PS.MethodInfo)
        self.assertEqual(res.access_modifier, F.AccessModifiers.Public)
        self.assertEqual(res.is_static, True)
        self.assertEqual(res.args, [['int[] a'], ['S<int, int> b']])
        self.assertEqual(res.data_type, ['void'])
        self.assertEqual(res.name, ['part'])

    def test_abstract(self):
        strings = ['internal', 'abstract', 'string', 'abst(', 'int[]',
                   'a', ',', 'S', '<', 'int', ',', 'int', '>', 'b', ');']
        parser = Parser.Parser()
        parser.curr_elem = PS.ClassInfo(None, 'class test')
        for string in strings:
            parser.parse_line(string)
        res = parser.curr_elem.methods.pop()
        self.assertEqual(type(res), PS.MethodInfo)
        self.assertEqual(res.access_modifier, F.AccessModifiers.Internal)
        self.assertEqual(
            res.args, [['int[]', 'a'], ['S', '<', 'int', ',', 'int', '>', 'b']]
        )
        self.assertEqual(res.data_type, ['string'])
        self.assertEqual(res.name, ['abst'])

    def test_extern(self):
        strings = ['protected internal extern Dict<int, int> ex();']
        parser = Parser.Parser()
        parser.curr_elem = PS.ClassInfo(None, 'class test')
        for string in strings:
            parser.parse_line(string)
        res = parser.curr_elem.methods.pop()
        self.assertEqual(type(res), PS.MethodInfo)
        self.assertEqual(
            res.access_modifier, F.AccessModifiers.ProtectedInternal
        )
        self.assertEqual(res.args, [])
        self.assertEqual(res.data_type, ['Dict<int,', 'int>'])
        self.assertEqual(res.name, ['ex'])

    def test_virtual(self):
        strings = ['virtual int virt();']
        parser = Parser.Parser()
        parser.curr_elem = PS.ClassInfo(None, 'class test')
        for string in strings:
            parser.parse_line(string)
        res = parser.curr_elem.methods.pop()
        self.assertEqual(type(res), PS.MethodInfo)
        self.assertEqual(res.access_modifier, F.AccessModifiers.Empty)
        self.assertEqual(res.args, [])
        self.assertEqual(res.data_type, ['int'])
        self.assertEqual(res.name, ['virt'])

    def test_field1(self):
        strings = ['example<int>', '.', 'subclass<int> asihfb;']
        parser = Parser.Parser()
        parser.curr_elem = PS.ClassInfo(None, 'class test')
        for string in strings:
            parser.parse_line(string)
        res = parser.curr_elem.fields.pop()
        self.assertEqual(type(res), PS.FieldInfo)
        self.assertEqual(res.is_delegate, False)
        self.assertEqual(res.value, [])
        self.assertEqual(res.data_type, ['example<int>', '.', 'subclass<int>'])
        self.assertEqual(res.name, 'asihfb')

    def test_field2(self):
        strings = ['example<int>', '.',
                   'subclass<int> asihfb = new example<int>.subclass<int>();']
        parser = Parser.Parser()
        parser.curr_elem = PS.ClassInfo(None, 'class test')
        for string in strings:
            parser.parse_line(string)
        res = parser.curr_elem.fields.pop()
        self.assertEqual(type(res), PS.FieldInfo)
        self.assertEqual(res.is_delegate, False)
        self.assertEqual(res.value, [' = new example<int>.subclass<int>()'])
        self.assertEqual(res.data_type, ['example<int>', '.', 'subclass<int>'])
        self.assertEqual(res.name, 'asihfb')

    def test_field3(self):
        strings = ['string test = "something" + "something";']
        parser = Parser.Parser()
        parser.curr_elem = PS.ClassInfo(None, 'class test')
        for string in strings:
            parser.parse_line(string)
        res = parser.curr_elem.fields.pop()
        self.assertEqual(type(res), PS.FieldInfo)
        self.assertEqual(res.value, [' = "something" + "something"'])
        self.assertEqual(res.data_type, ['string'])
        self.assertEqual(res.name, 'test')

    def test_incorrect1(self):
        strings = ['protected internal Dict<int, int> ex();']
        parser = Parser.Parser()
        parser.curr_elem = PS.ClassInfo(None, 'class test')
        for string in strings:
            parser.parse_line(string)

        self.assertEqual(parser.curr_elem.fields, [])

    def test_incorrect2(self):
        strings = ['protected internal partial Dict<int, int> e!x();']
        exc = None
        parser = Parser.Parser()
        parser.curr_elem = PS.ClassInfo(None, 'class test')
        try:
            for string in strings:
                parser.parse_line(string)
        except E.ParseException as e:
            exc = e
        self.assertEqual(type(exc), E.WrongExpressionException)

    def test_incorrect3(self):
        strings = ['a = a() + b{};']
        parser = Parser.Parser()
        parser.curr_elem = PS.ClassInfo(None, 'class test')
        for string in strings:
            parser.parse_line(string)

        self.assertEqual(parser.curr_elem.fields, [])

    def test_incorrect4(self):
        strings = ['protected public internal partial Dict<int, int> ex();']
        exc = None
        parser = Parser.Parser()
        parser.curr_elem = PS.ClassInfo(None, 'class test')
        try:
            for string in strings:
                parser.parse_line(string)
        except E.ParseException as e:
            exc = e
        self.assertEqual(type(exc), E.WrongExpressionException)


class TestCsParser(unittest.TestCase):
    def test_comments(self):
        comments = ['#{arg1',
                    '//arg2',
                    '/*arg3}*/',
                    'arg1+ ardg2/*arg3}*/',
                    '/*arg3}*/']
        parser = Parser.Parser()
        parser.curr_elem = PS.EnumInfo(None, 'enum test')
        for comment in comments:
            parser.parse_line(comment)
        self.assertEqual(parser.previous_lines, ['arg1+ ardg2'])
