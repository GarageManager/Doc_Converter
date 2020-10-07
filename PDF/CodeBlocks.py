import ProjectStructure as PS
import Tools.Functions as F
from Tools.Classes import TextParams
from Tools.Enums import Fonts, AccessModifiers


class Wrapper:
    def __init__(self, padding, bg_colour, border_color):
        self.padding = padding
        self.bg_colour = bg_colour
        self.border_color = border_color


class CodeBlocksMaker:
    def __init__(self, element, fonts):
        self._element = element
        self._fonts = fonts
        self.words = []
        self._curr_font = self._fonts[Fonts.CodeBlock]
        self.wrapper = Wrapper(
            10,
            F.rgb_to_non_linear(46, 46, 46),
            F.rgb_to_non_linear(69, 69, 69)
        )

        if self._element.access_modifier != AccessModifiers.Empty:
            self._add_word(
                F.access_modifier_to_string(self._element.access_modifier)
            )
        if self._element.is_static:
            self._add_word('static ')

        if isinstance(self._element, PS.Method):
            self._add_method()
        elif isinstance(self._element, PS.PropertyInfo):
            self._add_property()
        elif isinstance(self._element, PS.FieldInfo):
            self._add_field()
        else:
            self._add_container()

    def _add_method(self):
        self._curr_font = self._fonts[Fonts.CodeBlock]

        if self._element.is_async:
            self._add_word('async ')
        if self._element.is_delegate:
            self._add_word('delegate ')
        if self._element.is_partial:
            self._add_word('partial ')
        if self._element.is_extern:
            self._add_word('extern ')
        if self._element.is_virtual:
            self._add_word('virtual ')
        if self._element.is_abstract:
            self._add_word('abstract ')
        if self._element.is_override:
            self._add_word('override ')
        if self._element.is_event:
            self._add_word('event ')

        if self._element.data_type:
            for word in F.format_data_type(self._element.data_type):
                self._add_word(word)

        if self._element.is_operator:
            self._add_word('operator ')
        self._curr_font = self._fonts[Fonts.CodeBlockName]
        self._add_word(self._element.name)

        if not self._element.is_event:
            self._curr_font = self._fonts[Fonts.CodeBlockDefault]
            self._add_word('(')
            if self._element.args:
                for i, arg in enumerate(self._element.args):
                    arg_type, arg_name = F.format_argument(arg)
                    self._curr_font = self._fonts[Fonts.CodeBlock]
                    for word in arg_type:
                        self._add_word(word)
                    self._curr_font = self._fonts[Fonts.CodeBlockDefault]
                    self._add_word(arg_name)
                    if i != len(self._element.args) - 1:
                        self._add_word(', ')
            self._add_word(')')

    def _add_container(self):
        container_type = 'enum '
        if isinstance(self._element, PS.ClassInfo):
            if self._element.is_abstract:
                self._add_word('abstract ')
            if self._element.is_partial:
                self._add_word('partial ')
            if self._element.is_sealed:
                self._add_word('sealed ')
            container_type = 'class '
        elif isinstance(self._element, PS.InterfaceInfo):
            if self._element.is_partial:
                self._add_word('partial ')
            container_type = 'interface '
        elif isinstance(self._element, PS.StructInfo):
            if self._element.is_const:
                self._add_word('const ')
            if self._element.is_readonly:
                self._add_word('readonly ')
            container_type = 'struct '

        self._add_word(container_type)
        self._curr_font = self._fonts[Fonts.CodeBlockName]
        self._add_word(self._element.name)

        self._curr_font = self._fonts[Fonts.CodeBlock]
        if not isinstance(self._element, PS.EnumInfo):
            generic_info = F.format_data_type(self._element.generic_info)
            for word in generic_info:
                self._add_word(word)

    def _add_field(self):
        if self._element.is_const:
            self._add_word('const ')
        if self._element.is_readonly:
            self._add_word('readonly ')
        if self._element.data_type:
            for word in F.format_data_type(self._element.data_type):
                self._add_word(word)
        self._curr_font = self._fonts[Fonts.CodeBlockName]
        self._add_word(self._element.name)

    def _add_property(self):
        if self._element.is_virtual:
            self._add_word('virtual ')
        if self._element.is_abstract:
            self._add_word('abstract ')
        if self._element.is_override:
            self._add_word('override ')
        if self._element.data_type:
            for word in F.format_data_type(self._element.data_type):
                self._add_word(word)
        self._curr_font = self._fonts[Fonts.CodeBlockName]
        self._add_word(self._element.name)
        self._curr_font = self._fonts[Fonts.CodeBlockDefault]
        self._add_word('{ ')
        if self._element.has_get_value:
            self._add_access_method('get', self._element.private_get)
        if self._element.has_set_value:
            self._add_access_method('set', self._element.private_set)
        self._add_word('}')

    def _add_access_method(self, access_method, is_private):
        if is_private:
            self._curr_font = self._fonts[Fonts.CodeBlockDefault]
            self._add_word('private ')
        self._curr_font = self._fonts[Fonts.CodeBlockName]
        self._add_word(access_method)
        self._curr_font = self._fonts[Fonts.CodeBlockDefault]
        self._add_word('; ')

    def _add_word(self, word):
        self.words.append(TextParams(word, self._curr_font))
