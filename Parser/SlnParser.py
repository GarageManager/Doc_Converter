import os
import re
import Parser

def parse(path, encoding):
    out_files = []
    full_path = path
    path, name = os.path.split(path)

    with open(full_path,
              mode="r",
              errors='replace',
              encoding=encoding) as f:
        data = f.read()
        files = re.findall(
            r'[^\w]Project[^\w][\w\W]*?"([^\s,]*.csproj)"', data
        )

        for file in files:
            file = file.replace('\\\\', '/').replace('\\', '/')
            out_files.extend(
                Parser.CsprojParser.parse(f'{path}/{file}', encoding)
            )
    return out_files
