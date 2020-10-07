import os
import re
import Parser


class SlnParser:
    @staticmethod
    def parse(path, encodings):
        out_files = []
        full_path = path
        path, name = os.path.split(path)

        for encoding in encodings:
            try:
                with open(full_path, mode="r", encoding=encoding) as f:
                    data = f.read()
                    break
            except UnicodeEncodeError:
                pass
        else:
            with open(full_path, mode="r", encoding=encodings[0],
                      errors='replace') as f:
                data = f.read()
        files = re.findall(
            r'[^\w]Project[^\w][\w\W]*?"([^\s,]*.csproj)"', data
        )

        for file in files:
            file = file.replace('\\\\', '/').replace('\\', '/')
            out_files.extend(
                Parser.CsprojParser.parse(f'{path}/{file}', encodings)
            )
        return out_files
