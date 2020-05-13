import os
import Parser


class CsprojParser:
    def __init__(self):
        self.path = ''
        self.files = []

    def parse(self, path, encoding):
        self.path = path
        files = []

        for el in Parser.XmlParser.from_file(self.path).data.getroot().iter():
            _, _, tag = el.tag.rpartition('}')
            if tag == 'Compile':
                if 'Include' in el.attrib:
                    file = el.attrib["Include"]\
                        .replace('\\\\', '/')\
                        .replace('\\', '/')
                    files.append(f'{os.path.split(self.path)[0]}/{file}')

        for file_path in files:
            _, extension = os.path.splitext(file_path)
            if extension == '.cs':
                files.append(Parser.CsParser().parse(file_path, encoding))

        return files
