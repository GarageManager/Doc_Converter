#!/usr/bin/env python3
import os
import select
import sys
import argparse
from os.path import isdir

import Parser


def main():
    # Лучшей(да и вообще какого-то другой) проверки пуст ли входной поток
    # я не нашел(да и работает этот способ только на Unix системах)
    # по-другому не знаю как одновременно реализовать и пайпу, и наличие
    # одного обязательного аргумена
    if not select.select([sys.stdin, ], [], [], 0.0)[0]:
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('--output', help='Output pdf file.')
        arg_parser.add_argument(
            '--encoding', help='Project or file encoding. Default: utf-8'
        )
        arg_parser.add_argument(
            'path', help='File(*.cs, *.csproj, *.sln) or project path.'
        )

        args = arg_parser.parse_args()
        path = args.path
        encoding = 'utf-8' if not args.encoding else args.encoding
        if args.output:
            _ = args.output

        if isdir(path):
            for r, d, f in os.walk(path):
                for file_path in f:
                    _, extension = os.path.splitext(file_path)
                    if extension == '.cs':
                        name = os.path.join(r, file_path)
                        _ = Parser.CsParser().parse_file(name, encoding)
        else:
            _, extension = os.path.splitext(path)
            if extension in ['.cs', '.sln', '.csproj']:
                if extension == '.cs':
                    _ = Parser.CsParser().parse_file(path, encoding)
                elif extension == '.sln':
                    _ = Parser.SlnParser().parse(path, encoding)
                else:
                    _ = Parser.CsprojParser().parse(path, encoding)
            else:
                pass
    else:
        _ = Parser.CsParser().parse_stdin(sys.stdin)


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as e:
        print(str(e))
