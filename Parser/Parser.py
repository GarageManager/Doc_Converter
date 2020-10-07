import os
import Parser as PS


class Parser:
    def __init__(self):
        self.parsed_files = []

    def parse_files(self, path, input_type, encodings):
        if input_type == 'dir':
            for r, d, f in os.walk(path):
                for file_path in f:
                    _, extension = os.path.splitext(file_path)
                    if extension == '.cs':
                        name = os.path.join(r, file_path)
                        self.parsed_files.append(
                            PS.CsParser().parse(name, encodings)
                        )
        else:
            if input_type in ['.cs', 'std']:
                self.parsed_files.append(PS.CsParser().parse(path, encodings))
            elif input_type == '.csproj':
                self.parsed_files.extend(
                    PS.CsprojParser().parse(path, encodings)
                )
            elif input_type == '.sln':
                self.parsed_files.extend(PS.SlnParser().parse(path, encodings))

        return self.parsed_files
