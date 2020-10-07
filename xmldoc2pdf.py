#!/usr/bin/env python3
import os
import sys
import argparse
from os.path import isdir

from Parser import Parser
from PDF.PDFMaker import PDFMaker as PDF
from Tools.Exceptions import WrongExtensionException


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '--output',
        help='Output pdf file.',
        default=sys.stdout
    )
    arg_parser.add_argument(
        '--encoding',
        nargs='*',
        help='Project or file encoding. Default: utf-8',
        default=['utf-8', 'cp1251']
    )
    arg_parser.add_argument(
        'path',
        nargs='?',
        default=None,
        help='File(*.cs, *.csproj, *.sln) or project path.'
    )

    args = arg_parser.parse_args()
    path = args.path
    encoding = args.encoding
    output = args.output

    if args.path is None:
        parsed_files = Parser().parse_files(None, 'std', encoding)
    else:
        if isdir(path):
            parsed_files = Parser().parse_files(path, 'dir', encoding)
        else:
            _, extension = os.path.splitext(path)
            if extension in ['.cs', '.sln', '.csproj']:
                parsed_files = Parser().parse_files(path, extension, encoding)
            else:
                raise WrongExtensionException

    pdf = PDF(parsed_files)
    pdf.write_pdf(output)


def test():

    parsed_files = Parser().parse_files('/Users/aliser/Desktop/NSimulator', 'dir', ['utf-8', 'cp1251'])
    pdf = PDF(parsed_files)
    pdf.write_pdf('output.pdf')


if __name__ == "__main__":
    # try:
        test()
    # except Exception as e:
        # print(str(e), file=sys.stderr)
        # raise SystemExit(1)
