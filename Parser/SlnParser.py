import os
import re
from Parser import CsprojParser


class SlnParser:
    def __init__(self):
        self.full_path = ''
        self.path = ''
        self.name = ''
        self.encoding = ''

    def parse(self, path, encoding):
        self.full_path = path
        self.path, self.name = os.path.split(path)
        self.encoding = encoding

        with open(self.full_path,
                  mode="r",
                  errors='replace',
                  encoding=self.encoding) as f:
            data = f.read()
            files = re.findall(
                '[^\w]Project[^\w][\w\W]*?"([^\s,]*.csproj)"', data
            )

            for file in files:
                file = file.replace('\\\\', '/').replace('\\', '/')
                _ = CsprojParser().parse(f'{self.path}/{file}', self.encoding)
