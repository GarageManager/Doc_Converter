from PDF.Body import Body


class PDFMaker:
    def __init__(self, parsed_files):
        self._object_counter = 0
        self._objects_offset = []
        self._xref_offset = 0

        self._header = ''
        self._body = None
        self._xref = []
        self._trailer = ''
        self._start_xref = ''

        self._add_header()
        self._add_body(parsed_files)
        self._add_xref()
        self._add_trailer()
        self._add_start_xref()

    def _add_header(self):
        self._header = '%PDF-1.7\r\n'

    def _add_body(self, files):
        self._body = Body(files)

    def _add_xref(self):
        self._body.objects.sort(key=lambda x: x.number)
        self._count_offsets()
        self._xref = [f'xref\r\n'
                      f'0 {len(self._body.objects) + 1}\r\n'
                      f'0000000000 65535 f\r\n', ]
        for obj in self._body.objects:
            self._xref.append(
                f'{str(obj.offset).zfill(10)} 00000 n\r\n'
            )

    def _count_offsets(self):
        if self._body.objects:
            self._body.objects[0].offset = 10
            for i in range(1, len(self._body.objects)):
                self._body.objects[i].offset = (
                        self._body.objects[i - 1].offset +
                        len(self._body.objects[i - 1])
                )
            self._xref_offset = (self._body.objects[-1].offset
                                 + len(self._body.objects[-1]))
        else:
            pass

    def _add_trailer(self):
        self._trailer = (f'trailer\r\n<<\r\n'
                         f'/Size {len(self._body.objects) + 1}\r\n'
                         f'/Root 1 0 R\r\n>>\r\n')

    def _add_start_xref(self):
        self._start_xref = f'startxref\r\n{self._xref_offset}\r\n'

    def __str__(self):
        return f'{self._header}' \
               f'{str(self._body)}' \
               f'{"".join(self._xref)}' \
               f'{self._trailer}' \
               f'{self._start_xref}' \
               f'%%EOF'

    def write_pdf(self, output):
        if type(output) == str:
            with open(output, 'wb') as file:
                file.write(str(self).encode('latin-1'))
        else:
            output.buffer.write(str(self).encode('latin-1'))
