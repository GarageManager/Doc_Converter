from fpdf.php import UTF8StringToArray

from PDF.Page import Page
from Tools import Functions
from Tools.Enums import Fonts
from Tools.Classes import TextParams, Lines, Link
from PDF.CodeBlocks import CodeBlocksMaker


def sort_key(element):
    return element.obj.name


class ObjectWithXmlContent:
    def __init__(self, obj):
        self.obj = obj
        self.namespaces = []
        self.fields = []
        self.properties = []
        self.methods = []
        self.delegates = []
        self.events = []
        self.classes = []
        self.structs = []
        self.enums = []
        self.interfaces = []
        self.constructors = []

    def __bool__(self):
        if (self.namespaces or self.fields or self.properties or self.enums
                or self.methods or self.classes or self.structs or self.events
                or self.interfaces or self.delegates or self.obj.xml):
            return True
        return False


class Column:
    def __init__(self, text, pos_x, pos_y, width, is_xml):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.width = width
        self.text = text
        self.is_xml = is_xml


class Pages:
    def __init__(self, start_number, parent_num, resources_num, files, fpdf,
                 fonts):
        self.pages = []
        self._resources_num = resources_num
        self._parent_num = parent_num
        self._fpdf = fpdf
        self._fonts = fonts
        self._curr_page_num = -1
        self._start_number = start_number
        self._see_also = []
        self._padding = 0
        self._wrapper = None
        self._start_pos_x = Page.PADDING
        self._line_width = Page.CONTENT_WIDTH
        self._available_width = self._line_width
        self._xml_list_type = 0
        self._xml_tag_content = []
        self._links = []
        self._contents_page_num = []

        self._add_cs_files(files)

    def get_pages_data(self):
        objects = []
        for page in self.pages:
            objects.extend(page.get_page_data())
        return objects

    def _add_page(self):
        self._fpdf.set_font(self._fonts[Fonts.PageNumber].name)
        num = (self.pages[self._curr_page_num].number + 2 if self.pages
               else self._start_number)
        self._curr_page_num += 1
        self.pages.append(
            Page(num, self._parent_num, self._resources_num,
                 self._curr_page_num + 1, self._fonts[Fonts.PageNumber],
                 self._fpdf)
        )
        self.pages[self._curr_page_num].available_height -= self._padding

    def _add_cs_files(self, files):
        if not files:
            self._add_page()
            return

        files_with_xml_content = []
        for file in files:
            content = self._get_content_with_xml(file)
            if content:
                files_with_xml_content.append(content)

        if not files_with_xml_content:
            self._add_page()
            return

        files_with_xml_content.sort(key=sort_key)
        content = [TextParams(elem.obj.name, self._fonts[Fonts.Item])
                   for elem in files_with_xml_content]

        self._prepare_table_of_content(content)
        for i, file in enumerate(files_with_xml_content):
            self._add_page()
            self._contents_page_num.append(self._curr_page_num)
            self._add_element(
                file.obj, self._fonts[Fonts.Filename], 'File'
            )
            self._add_content(file)
        self._add_table_of_content(content)

    def _prepare_table_of_content(self, table_content):
        page_content_height = Page.PAGE_HEIGHT - Page.PADDING * 2
        line_height = table_content[0].font.line_height
        title_height = self._fonts[Fonts.Title].line_height + 20
        lines_counter = 0

        self._set_text_block_params(
            Page.CONTENT_WIDTH - 130,
            Page.PADDING
        )

        for elem in table_content:
            lines_counter += len(self._align_text_to_page_width([elem, ]))
        available_height = page_content_height - title_height
        self._add_page()
        for i in range(lines_counter):
            available_height -= line_height + 12
            if available_height < 0:
                self._add_page()
                available_height = page_content_height - line_height - 12

    def _add_table_of_content(self, content):
        self._curr_page_num = 0
        self._add_title('Contents:', self._fonts[Fonts.Title], offset=20)
        for i, elem in enumerate(content):
            table_rows = []
            pos_y = self.pages[self._curr_page_num].available_height - 12

            if pos_y < Page.PADDING + self._fonts[Fonts.Item].line_height + 12:
                self._curr_page_num += 1
                pos_y = self.pages[self._curr_page_num].available_height - 12

            table_rows.append(Column(
                TextParams(
                    elem.text,
                    self._fonts[Fonts.Item],
                    is_link=True,
                    link=Link(
                        self.pages[self._contents_page_num[i]].number,
                        Page.PAGE_HEIGHT
                    )
                ),
                Page.PADDING, pos_y, 720,  False)
            )
            table_rows.append(
                Column(
                    TextParams(
                        str(self._contents_page_num[i]),
                        self._fonts[Fonts.Default],
                    ),
                    750, pos_y, 60, False)
            )
            self._add_table_row(table_rows)

    def _add_element(self, element, font, element_type):
        if element_type != 'Constructor':
            self._add_title(element.name, font, title_type=element_type)
        if element_type == 'File':
            self._add_line(0, Page.PAGE_WIDTH)
        if element_type not in ['File', 'Namespace']:
            self._add_code_blocks(element)
        self._add_xml_to_page(element.xml)

    def _get_content_with_xml(self, element):
        content = ObjectWithXmlContent(element)

        for namespace in element.namespaces:
            _content = self._get_content_with_xml(namespace)
            if namespace.xml or _content:
                content.namespaces.append(_content)

        for field in element.fields:
            if field.xml:
                content.fields.append(field)
        for prop in element.properties:
            if prop.xml:
                content.properties.append(ObjectWithXmlContent(prop))

        for enum in element.enums:
            fields_has_xml = False
            for field in enum.enum_fields:
                if field[0]:
                    fields_has_xml = True
                    break
            if enum.xml or fields_has_xml:
                content.enums.append(ObjectWithXmlContent(enum))
        for class_item in element.classes:
            _content = self._get_content_with_xml(class_item)
            if class_item.xml or _content:
                content.classes.append(_content)
        for struct in element.structs:
            _content = self._get_content_with_xml(struct)
            if struct.xml or _content:
                content.structs.append(_content)
        for interface in element.interfaces:
            _content = self._get_content_with_xml(interface)
            if interface.xml or _content:
                content.interfaces.append(_content)

        for constructor in element.constructors:
            if constructor.xml:
                content.constructors.append(ObjectWithXmlContent(constructor))
        for method in element.methods:
            if method.xml:
                content.methods.append(ObjectWithXmlContent(method))
        for delegate in element.delegates:
            if delegate.xml:
                content.delegates.append(ObjectWithXmlContent(delegate))
        for event in element.events:
            if event.xml:
                content.events.append(ObjectWithXmlContent(event))
        return content

    def _add_content(self, content):
        self._add_constructors(content.constructors)
        self._add_list('Enums:', content.enums)
        self._add_list('Classes:', content.classes)
        self._add_list('Structures:', content.structs)
        self._add_list('Interfaces:', content.interfaces)
        self._add_list('Methods:', content.methods)
        self._add_list('Events:', content.events)
        self._add_list('Delegates:', content.delegates)
        self._add_fields(content.fields)
        self._add_properties(content.properties)

        for namespace in content.namespaces:
            self._add_element(namespace.obj, self._fonts[Fonts.ObjectName],
                              'Namespace')
            self._add_content(namespace)
        for class_obj in content.classes:
            self._add_element(class_obj.obj, self._fonts[Fonts.ObjectName],
                              'Class')
            self._add_content(class_obj)
        for interface in content.interfaces:
            self._add_element(interface.obj, self._fonts[Fonts.ObjectName],
                              'Interface')
            self._add_content(interface)
        for struct in content.structs:
            self._add_element(struct.obj, self._fonts[Fonts.ObjectName],
                              'Struct')
            self._add_content(struct)
        for enum in content.enums:
            self._add_enum(enum.obj)
        for elem in content.methods:
            self._add_method('Method', elem.obj)
        for elem in content.events:
            self._add_method('Event', elem.obj)
        for elem in content.delegates:
            self._add_method('Delegate', elem.obj)

        self._add_see_also()

    def _add_method(self, method_type, method):
        self._add_element(method, self._fonts[Fonts.ObjectName], method_type)
        self._add_see_also()

    def _add_constructors(self, constructors):
        if not constructors:
            return
        self._add_title('Constructors:', self._fonts[Fonts.Title], offset=15)
        for constructor in constructors:
            self._add_method('Constructor', constructor.obj)
        self._add_see_also()

    def _add_enum(self, enum):
        self._add_element(enum, self._fonts[Fonts.ObjectName], 'Enum')

        self._add_title('Fields', self._fonts[Fonts.Title])
        for field in enum.enum_fields:
            table_row = []
            pos_y = self.pages[self._curr_page_num].available_height - 12
            field_data = [s.strip() for s in ''.join(field[1]).split('=')]
            if len(field_data) == 1:
                name = field_data[0]
                num = ''
            else:
                name, num = field_data
            table_row.append(Column(
                TextParams(name, self._fonts[Fonts.Item]),
                Page.PADDING, pos_y, 150, False)
            )
            table_row.append(Column(
                TextParams(num, self._fonts[Fonts.Default]),
                170 + Page.PADDING, pos_y, 80, False)
            )
            table_row.append(Column(
                TextParams(field[0], self._fonts[Fonts.Default]),
                270, pos_y, 540 - Page.PADDING, True)
            )
            self._add_table_row(table_row)

    def _add_properties(self, properties_list):
        properties = {'Indexers': [], 'Properties': []}
        for prop in properties_list:
            if prop.obj.is_indexer:
                properties['Indexers'].append(prop)
            else:
                properties['Properties'].append(prop)

        self._add_list('Properties:', properties['Properties'])
        self._add_list('Indexers:', properties['Indexers'])

        for key in properties.keys():
            if properties[key]:
                self._add_title(f'{key}:', self._fonts[Fonts.ObjectName])
                for prop in properties[key]:
                    self._add_code_blocks(prop.obj)
                    self._add_xml_to_page(prop.obj.xml)

    def _add_fields(self, fields):
        if not fields:
            return
        self._add_title('Fields:', self._fonts[Fonts.Title], offset=15)
        for field in fields:
            self._add_code_blocks(field)
            self._add_xml_to_page(field.xml)

    def _add_code_blocks(self, element):
        blocks = CodeBlocksMaker(element, self._fonts)
        self._wrapper = blocks.wrapper
        self._padding = blocks.wrapper.padding
        self._set_text_block_params(
            Page.CONTENT_WIDTH - self._padding * 2,
            Page.PADDING + self._padding
        )
        self._add_text_to_page(
            blocks.words,
            self._fonts[Fonts.CodeBlockDefault],
            self.pages[self._curr_page_num].available_height - self._padding,
            self._curr_page_num
        )
        self._wrapper = None

    def _add_list(self, list_name, lst):
        if not lst:
            return
        self._add_title(list_name, self._fonts[Fonts.Title], offset=20)
        for item in lst:
            _item = item.obj
            table_rows = []
            if list_name in ['Methods:', 'Delegates:']:
                args = []
                for arg in _item.args:
                    formatted = Functions.format_argument(arg)
                    args.append(f'{"".join(formatted[0])}{formatted[1]}')
                name = f'{_item.name}({", ".join(args)})'
            else:
                name = _item.name
            pos_y = self.pages[self._curr_page_num].available_height - 12

            table_rows.append(Column(
                TextParams(name, self._fonts[Fonts.Item]),
                Page.PADDING, pos_y, 260, False)
            )
            table_rows.append(Column(
                TextParams(_item.xml, self._fonts[Fonts.Default]),
                300, pos_y, 510, True)
            )
            self._add_table_row(table_rows)
        self.pages[self._curr_page_num].add_offset(30)

    def _add_table_row(self, table_row):
        if (table_row[0].pos_y
                < Page.PADDING + table_row[0].text.font.line_height + 12):
            self._add_page()
            for col in table_row:
                col.pos_y = (self.pages[self._curr_page_num].available_height
                             - 12)
        self._add_line(Page.PADDING, Page.CONTENT_WIDTH)
        page_num = self._curr_page_num
        for column in table_row:
            self._set_text_block_params(column.width, column.pos_x)
            if column.is_xml:
                if not column.text.text:
                    continue
                for child in column.text.text:
                    if child.tag == 'summary':
                        self._get_tag_content(child)
                        self._add_tag_content(
                            column.pos_y, page_num, column.text.font
                        )
                        break
            else:
                self._add_text_to_page(
                    [column.text, ],
                    column.text.font,
                    column.pos_y,
                    page_num
                )

    def _add_xml_to_page(self, xml):
        font = self._fonts[Fonts.Default]
        offset = 30
        if not xml:
            return
        has_parameters = False
        has_parameter_types = False
        has_exceptions = False

        for content in xml:
            if content.tag == 'c':
                self._xml_tag_content.append(
                    TextParams(content.data[0], self._fonts[Fonts.DefaultBold])
                )
                self._get_tag_content(content)
            elif content.tag == 'see':
                if self._xml_tag_content:
                    string = ' ' + content.attributes["cref"]
                else:
                    string = content.attributes["cref"]
                self._xml_tag_content.append(
                    TextParams(string, self._fonts[Fonts.XMLLink])
                )
                self._get_tag_content(content)
            elif content.tag == 'paramref':
                self._xml_tag_content.append(TextParams(
                    'parameter ', self._fonts[Fonts.Default]
                ))
                self._xml_tag_content.append(TextParams(
                    content.attributes["name"] + ' ',
                    self._fonts[Fonts.XMLName]
                ))
                self._get_tag_content(content)
            elif content.tag == 'typeparamref':
                self._xml_tag_content.append(TextParams(
                    'parameter type ', self._fonts[Fonts.Default]
                ))
                self._xml_tag_content.append(TextParams(
                    content.attributes["name"] + ' ',
                    self._fonts[Fonts.XMLName]
                ))
                self._get_tag_content(content)
            elif content.tag == 'seealso':
                self._see_also.append(content.attributes['cref'])
            elif content.tag == 'list':
                self._add_xml_list(content)
            elif content.tag == 'item':
                self._get_tag_content(content)
            elif content.tag == 'term':
                self._get_tag_content(content)
            elif content.tag == 'description':
                self._get_tag_content(content)
            elif content.tag == 'code':
                self._xml_tag_content.append(
                    TextParams('\n', self._fonts[Fonts.Default])
                )
                self._xml_tag_content.append(
                    TextParams(content.data[0], self._fonts[Fonts.DefaultBold])
                )
                if content.data[1:]:
                    self._xml_tag_content.append(
                        TextParams('\n', self._fonts[Fonts.Default])
                    )
                    for text in content.data[1:]:
                        self._xml_tag_content.append(
                            TextParams(text, self._fonts[Fonts.Default])
                        )
                self._add_tag_content(
                    self.pages[self._curr_page_num].available_height,
                    self._curr_page_num,
                    font
                )
                self.pages[self._curr_page_num].add_offset(20)
            elif content.tag == 'inheritdoc':
                self._xml_tag_content.append(
                    TextParams(content.tag, self._fonts[Fonts.Default])
                )
                self._add_tag_content(
                    self.pages[self._curr_page_num].available_height,
                    self._curr_page_num,
                    self._fonts[Fonts.Default]
                )
                self.pages[self._curr_page_num].add_offset(offset)
            else:
                if content.tag == 'exception':
                    if has_parameter_types or has_parameters:
                        self.pages[self._curr_page_num].add_offset(20)
                    if not has_exceptions:
                        self._add_title(
                            'Exceptions', self._fonts[Fonts.XMLTitle],
                            offset=10
                        )
                        has_exceptions = True
                    offset = 10
                elif content.tag == 'param':
                    if has_parameter_types or has_exceptions:
                        self.pages[self._curr_page_num].add_offset(20)
                    if not has_parameters:
                        self._add_title(
                            'Parameters', self._fonts[Fonts.XMLTitle],
                            offset=10
                        )
                        has_parameters = True
                    offset = 10
                elif content.tag == 'typeparam':
                    if has_parameters or has_exceptions:
                        self.pages[self._curr_page_num].add_offset(20)
                    if not has_parameter_types:
                        self._add_title(
                            'Parameter types', self._fonts[Fonts.XMLTitle],
                            offset=10
                        )
                        has_parameter_types = True
                    offset = 10
                elif (content.tag in ['returns', 'value', 'remarks']
                      and content.tag != 'summary'):
                    if has_parameter_types or has_parameters or has_exceptions:
                        self.pages[self._curr_page_num].add_offset(20)
                    text = content.tag[0].upper() + content.tag[1:]
                    self._add_title(
                        text, self._fonts[Fonts.XMLTitle], offset=10
                    )
                elif content.tag == 'para':
                    offset = 0

                self._add_tag_attributes(content)
                self._get_tag_content(content)
                self._add_tag_content(
                    self.pages[self._curr_page_num].available_height,
                    self._curr_page_num,
                    font
                )
                self.pages[self._curr_page_num].add_offset(offset)

        if has_parameter_types or has_parameters or has_exceptions:
            self.pages[self._curr_page_num].add_offset(20)

    def _add_xml_list(self, xml_list):
        list_type = xml_list.attributes['type']
        counter = 0
        self._xml_tag_content.append(
            TextParams('\n', self._fonts[Fonts.Default])
        )
        for item in xml_list.data:
            counter += 1
            marker = '• ' if list_type == 'bullet' else f'{counter}) '
            self._xml_tag_content.append(
                TextParams(marker, self._fonts[Fonts.Default])
            )
            self._get_tag_content(item)
            self._xml_tag_content.append(
                TextParams('\n', self._fonts[Fonts.Default])
            )

    def _add_tag_attributes(self, content):
        for attribute in content.attributes:
            if content.tag == 'param':
                s = f'parameter {attribute}: {content.attributes[attribute]}'
            elif content.tag == 'typeparam':
                s = f'type {attribute}: {content.attributes[attribute]}'
            elif content.tag == 'exception':
                s = f'exception: {content.attributes[attribute]}'
            else:
                s = f'{attribute}: {content.attributes[attribute]}'
            self._set_text_block_params(Page.CONTENT_WIDTH, Page.PADDING)
            self._add_text_to_page(
                [TextParams(s, self._fonts[Fonts.DefaultBold]), ],
                self._fonts[Fonts.DefaultBold],
                self.pages[self._curr_page_num].available_height,
                self._curr_page_num
            )

    def _get_tag_content(self, content):
        if content.tag == 'c':
            content.data = content.data[1:]
        for elem in content.data:
            indent = 0
            if content.tag == 'param' or content.tag == 'typeparam':
                indent = 20
            if type(elem) is str:
                self._set_text_block_params(
                    self._line_width - indent, self._start_pos_x + indent
                )
                self._xml_tag_content.append(
                    TextParams(f'{elem} ', self._fonts[Fonts.Default])
                )
            else:
                self._add_xml_to_page([elem, ])

    def _add_tag_content(self, pos_y, page_num, font):
        self._add_text_to_page(
            self._xml_tag_content, font, pos_y, page_num
        )
        self._xml_tag_content = []

    def _add_see_also(self):
        if self._see_also:
            self._add_title('See also', self._fonts[Fonts.Title], offset=10)
            self._set_text_block_params(
                Page.CONTENT_WIDTH - 20,
                Page.PADDING + 20
            )
            for list_elem in self._see_also:
                self._add_text_to_page(
                    [TextParams('• ' + list_elem, self._fonts[Fonts.Item]), ],
                    self._fonts[Fonts.Item],
                    self.pages[self._curr_page_num].available_height,
                    self._curr_page_num
                )
                self.pages[self._curr_page_num].add_offset(5)
            self._see_also = []

    def _set_text_block_params(self, line_width, start_pos_x):
        self._available_width = line_width
        self._line_width = line_width
        self._start_pos_x = start_pos_x

    def _add_title(self, name, font, offset=30, title_type=''):
        self._set_text_block_params(Page.CONTENT_WIDTH, Page.PADDING)
        self._add_text_to_page(
            [TextParams(f'{name} {title_type}', font), ],
            font,
            self.pages[self._curr_page_num].available_height,
            self._curr_page_num
        )
        self.pages[self._curr_page_num].add_offset(offset)

    def _add_line(self, pos_x, width):
        if self.pages[self._curr_page_num].available_height < 12:
            self._add_page()
        self.pages[self._curr_page_num].add_line(pos_x, width)

    def _add_text_to_page(self, text, font, pos_y, page_num):
        if not text:
            return
        lines = self._align_text_to_page_width(text)
        _lines = []
        first_line_pos = pos_y - font.line_height
        pos_y -= font.size

        for line in lines:
            if pos_y < Page.PADDING + self._padding:
                self._add_lines_to_page(
                    _lines, font.line_height, first_line_pos, page_num
                )
                if page_num == len(self.pages) - 1:
                    self._add_page()
                    pos_y = self.pages[self._curr_page_num].available_height
                else:
                    pos_y = Page.PAGE_HEIGHT - Page.PADDING
                pos_y -= font.size
                page_num += 1
                _lines = []
                first_line_pos = pos_y
            pos_y -= font.line_height
            _lines.append(line)
        self._add_lines_to_page(_lines, font.line_height, first_line_pos,
                                page_num)

    def _add_lines_to_page(self, lines, line_height, first_line_pos, page_num):
        new_available_height = first_line_pos
        if self._wrapper and lines:
            height = self._padding * 2 + len(lines) * line_height
            block_pos_y = (first_line_pos - (len(lines) - 1) * line_height
                           - self._padding - lines[0][0].font.bottom_padding)
            self.pages[page_num].add_wrapper(
                self._wrapper, height, block_pos_y
            )
            new_available_height -= self._padding + 30
        self.pages[page_num].add_text_lines_to_page(
            lines, self._start_pos_x, first_line_pos, line_height
        )
        new_available_height -= line_height * (len(lines) - 1)
        if new_available_height < self.pages[page_num].available_height:
            self.pages[page_num].available_height = new_available_height

    def _align_text_to_page_width(self, text):
        lines = Lines()
        for _text in text:
            self._fpdf.set_font(_text.font.name, size=_text.font.size)
            for uni in UTF8StringToArray(_text.text):
                self._fpdf.current_font['subset'].append(uni)
            text_width = Functions.get_string_width(
                _text.text, self._fpdf, Page.PAGE_WIDTH
            )
            word_start_pos = 0
            if text_width < self._available_width:
                split_text = _text.text.split('\n')
                if len(split_text) != 1:
                    lines.add_line(TextParams(split_text[0], _text.font))
                    for i in range(1, len(split_text)):
                        lines.add_new_line(
                            TextParams(split_text[i], _text.font,
                                       is_link=_text.is_link, link=_text.link)
                        )
                    self._available_width = self._line_width
                    text_width = Functions.get_string_width(
                        split_text[-1], self._fpdf, Page.PAGE_WIDTH
                    )
                    lines.lines[-1][-1].width = text_width
                else:
                    lines.add_line(
                        TextParams(split_text[0], _text.font, text_width,
                                   is_link=_text.is_link, link=_text.link)
                    )
                self._available_width -= text_width
            else:
                for i in range(len(_text.text)):
                    if _text.text[i].isspace():
                        if word_start_pos != i:
                            word = _text.text[word_start_pos:i+1]
                            lines = self._add_word_to_lines(
                                lines, word, _text.font, is_link=_text.is_link,
                                link=_text.link
                            )
                        if _text.text[i] == '\n':
                            lines.new_line = True
                        word_start_pos = i + 1
                if word_start_pos != len(_text.text):
                    word = _text.text[word_start_pos:]
                    lines = self._add_word_to_lines(
                        lines, word, _text.font,
                        is_link=_text.is_link, link=_text.link
                    )
        self._available_width = self._line_width
        return lines.lines

    def _add_word_to_lines(self, lines, word, font, is_link, link):
        word_width = Functions.get_string_width(
            word, self._fpdf, Page.PAGE_WIDTH
        )

        if word_width > self._available_width:
            if word_width <= self._line_width:
                lines.add_new_line(TextParams(
                    word, font, width=word_width, is_link=is_link, link=link
                ))
            else:
                split_word = Functions.split_word_to_width(
                    self._line_width,
                    self._available_width,
                    word,
                    font,
                    self._fpdf,
                    Page.PAGE_WIDTH
                )
                lines.add_line(split_word[0])
                for i in range(1, len(split_word)):
                    lines.add_new_line(split_word[i])
                word_width = Functions.get_string_width(
                    split_word[-1].text, self._fpdf, Page.PAGE_WIDTH
                )
            self._available_width = self._line_width
        else:
            lines.add_line(TextParams(
                word, font, width=word_width, is_link=is_link, link=link
            ))
        self._available_width -= word_width
        return lines
