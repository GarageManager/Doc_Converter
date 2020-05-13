import os
import re
from Parser import CsprojParser


class SlnParser:
    def __init__(self):
        self.full_path = ''
        self.path = ''
        self.name = ''

    def parse(self, path, encoding):
        out_files = []
        self.full_path = path
        self.path, self.name = os.path.split(path)

        with open(self.full_path,
                  mode="r",
                  errors='replace',
                  encoding=encoding) as f:
            data = f.read()
            files = re.findall(
                r'[^\w]Project[^\w][\w\W]*?"([^\s,]*.csproj)"', data
            )

            for file in files:
                file = file.replace('\\\\', '/').replace('\\', '/')
                out_files.append(
                    CsprojParser().parse(f'{self.path}/{file}', encoding)
                )
        return out_files
