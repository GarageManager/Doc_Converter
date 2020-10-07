from PDF.PDFObject import PDFObject as Object
from Tools.Functions import rgb_to_non_linear, escape, get_string_width
from fpdf.php import UTF8ToUTF16BE, UTF8StringToArray

from Tools.Classes import Link


class Page:
    BG_COLOR = rgb_to_non_linear(23, 23, 23)
    PAGE_WIDTH = 840
    PAGE_HEIGHT = 1188
    PADDING = 30
    CONTENT_WIDTH = PAGE_WIDTH - PADDING * 2

    def __init__(self, obj_number, parent_num, resources_num, page_num, font,
                 fpdf):
        self._parent_num = parent_num
        self._res_num = resources_num
        self.number = obj_number
        self.available_height = self.PAGE_HEIGHT - self.PADDING
        self.content = []
        self._words = []
        self._links = []

        self._add_background()
        self._add_page_num(page_num, font, fpdf)

    def add_offset(self, offset):
        self.available_height -= offset

    def get_page_data(self):
        return [
            Object(self.number, self._make_page_obj()),
            Object(self.number + 1, self._make_stream())
        ]

    def add_wrapper(self, wrapper, height, pos_y):
        self.content.append(
            f'1 w\r\n'
            f'{wrapper.bg_colour} rg\r\n'
            f'{wrapper.border_color} RG\r\n'
            f'{Page.PADDING} {pos_y} '
            f'{Page.CONTENT_WIDTH} {height} re\r\n'
            f'B\r\n'
        )

    def add_text_lines_to_page(self, lines, pos_x, pos_y, line_height):
        for line in lines:
            self.add_text_line_to_page(line, pos_x, pos_y)
            self._add_links_in_line(line, pos_x, pos_y)
            pos_y -= line_height

    def add_text_line_to_page(self, line, pos_x, pos_y):
        string_width = 0
        start_pos = 0
        offset = 0
        for i in range(1, len(line)):
            string_width += line[i - 1].width
            if line[i].font != line[i-1].font:
                string = ''.join([text.text for text in line[start_pos:i]])
                self.add_text_to_page(
                    string, line[i-1].font, pos_x + offset, pos_y
                )
                offset = string_width
                start_pos = i

        string = ''.join([text.text for text in line[start_pos:]])

        if start_pos == 0:
            offset = 0
        self.add_text_to_page(
            string, line[start_pos].font, pos_x + offset, pos_y
        )

    def add_text_to_page(self, string, font, pos_x, pos_y):
        self.content.append(
            f'BT\r\n'
            f'/{"F2" if font.bold else "F1"} {font.size} Tf\r\n'
            f'{pos_x} {pos_y} Td\r\n'
            f'{font.color} rg\r\n'
            f'({escape(UTF8ToUTF16BE(string, False))})Tj\r\n'
            f'ET\r\n'
        )

    def _add_links_in_line(self, line, pos_x, pos_y):
        prev_link = Link(-1, -1)
        line_height = line[-1].font.line_height
        pos_y -= line[-1].font.bottom_padding
        link_width = 0

        for text in line:
            if not text.link or text.link != prev_link:
                if prev_link:
                    self._add_link(prev_link, pos_x, pos_y, link_width,
                                   line_height)
                    pos_x += link_width
                if text.link:
                    prev_link = text.link
                    link_width = text.width
                else:
                    link_width = 0
                    prev_link = Link(-1, -1)
                    pos_x += text.width
            else:
                link_width += text.width
        if prev_link:
            self._add_link(prev_link, pos_x, pos_y, link_width, line_height)

    def _add_link(self, link, pos_x, pos_y, width, height):
        self._links.append(
            f'<</Type /Annot /Subtype /Link'
            f'/Rect [{pos_x} {pos_y} '
            f'{pos_x + width} {pos_y + height}] '
            f'/Border [0 0 0] '
            f'/Dest [{link.page} 0 R '
            f'/XYZ 0 {link.pos_y} null]>>')

    def add_line(self, pos_x, width):
        self.content.append(
            f'{rgb_to_non_linear(128, 128, 128)} RG\r\n'
            f'{pos_x} {self.available_height - 10} m '
            f'{pos_x + width} {self.available_height - 10} '
            f'l h S\r\n'
        )
        self.available_height -= 22

    def _add_background(self):
        self.content.append(
            f'{self.BG_COLOR} rg\r\n'
            f'0 0 {self.PAGE_WIDTH} {self.PAGE_HEIGHT} re\r\n'
            f'f\r\n'
        )

    def _add_page_num(self, number, font, fpdf):
        string = str(number)
        for uni in UTF8StringToArray(string):
            fpdf.current_font['subset'].append(uni)
        str_width = get_string_width(string, fpdf, self.PAGE_WIDTH)
        self.content.append(
            f'BT\r\n'
            f'/F1 {font.size} Tf\r\n'
            f'{self.PAGE_WIDTH - self.PADDING - str_width} '
            f'{self.PADDING - font.size} Td\r\n'
            f'{font.color} rg\r\n'
            f'({escape(UTF8ToUTF16BE(string, False))})Tj\r\n'
            f'ET\r\n'
        )

    def _make_page_obj(self):
        return f'<</Type /Page /Parent {self._parent_num} 0 R ' \
               f'/Resources {self._res_num} 0 R /MediaBox [0 0 840 1188] ' \
               f'/Contents [{self.number + 1} 0 R]' \
               f'{self._add_annotations() if self._links else ""}>>'

    def _add_annotations(self):
        return f' /Annots [{"".join(self._links)}]'

    def _make_stream(self):
        content = "".join(self.content)
        return f'<</Length {len(content)}>>\r\n' \
               f'stream\r\n' \
               f'{content}' \
               f'endstream'
