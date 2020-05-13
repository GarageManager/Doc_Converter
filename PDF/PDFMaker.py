# просто заглушка
import Parser
import os

FILE_HANDLER = {
    '.cs': Parser.CsParser().parse,
    '.csproj': Parser.CsprojParser().parse,
    '.sln': Parser.SlnParser().parse,
}


class PDFMaker:
    def __init__(self, path, input_type, output, encoding, std=None):
        if output:
            with open(output, 'w', encoding=encoding) as out_file:
                files = []

                if input_type in FILE_HANDLER.keys():
                    # files.extend(FILE_HANDLER[input_type](path, encoding))
                    FILE_HANDLER[input_type](path, encoding)
                elif input_type == 'std':
                    # files.extend(FILE_HANDLER[input_type](path, encoding, std))
                    FILE_HANDLER[input_type](path, encoding, std)
                elif input_type == 'dir':
                    for r, d, f in os.walk(path):
                        for file_path in f:
                            _, extension = os.path.splitext(file_path)
                            if extension == '.cs':
                                name = os.path.join(r, file_path)
                                # files.extend(
                                #     FILE_HANDLER[extension](name, encoding)
                                # )
                                FILE_HANDLER[extension](name, encoding)

                # for file in files:
                #     out_file.write(f'{str(file)}\n')