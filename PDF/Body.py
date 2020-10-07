from fpdf import FPDF

from PDF.Fonts import set_fonts
from PDF.PDFObject import PDFObject as Object
from PDF.Pages import Pages
from Tools.Enums import Fonts
from Tools.Regexes import GET_FONTS_INFO, GET_OBJECTS


class Body:
    def __init__(self, files):
        self.objects = []
        self._base_offset = 10
        self._pages_offset = 0
        self._fonts_counter = 0
        self._fpdf = None
        self._make_pages(files)

    def _set_fonts(self):
        self._fonts = set_fonts('DejaVu', 'DejaVu')
        self._fpdf = FPDF()
        self._add_font_to_fpdf(
            self._fpdf,
            self._fonts[Fonts.Default].name,
            'PDF/Fonts/DejaVuSansCondensed.ttf',
            True)
        self._add_font_to_fpdf(
            self._fpdf,
            self._fonts[Fonts.DefaultBold].name,
            'PDF/Fonts/DejaVuSansCondensed-Bold.ttf',
            True
        )

        self._resource_number = 3
        self._pages_start_index = 5 + self._fonts_counter * 7

    def _add_font_to_fpdf(self, pdf, font_name, font_path, is_unicode):
        pdf.add_font(font_name, '', font_path, uni=is_unicode)
        self._fonts_counter += 1

    def _add_fonts(self):
        buffer = self._fpdf.output('', 'S')
        fonts_info = GET_FONTS_INFO.findall(buffer)[0]
        objects = GET_OBJECTS.findall(fonts_info)

        for i in range(0, len(objects), 2):
            num = int(objects[i][1].split()[0])
            self.objects.append(Object(num, objects[i + 1][0]))
        resources = '<<\r\n/Font <<\r\n'
        for i in range(self._fonts_counter):
            resources += f'/F{i + 1} {5 + i * 7} 0 R\r\n'
        resources += '>>\r\n>>\r\n'
        self.objects.append(Object(3, resources))

    def _make_pages(self, files):
        self.objects.append(Object(1, '<</Type /Catalog /Pages 2 0 R>>'))
        self._set_fonts()

        pages = Pages(self._pages_start_index, 5, self._resource_number, files,
                      self._fpdf, self._fonts)

        self.objects.append(Object(
            2, f'<</Type /Pages '
               f'/Kids [{" ".join([f"{p.number} 0 R" for p in pages.pages])}] '
               f'/Count {len(pages.pages)}>>'
        ))

        self.objects.extend(pages.get_pages_data())
        self._add_fonts()
        self._add_info()

    def _add_info(self):
        self.objects.append(Object(4, '/Producer Alisher Kazantcev'))

    def __str__(self):
        return ''.join(map(str, self.objects))
