#!/usr/bin/env python3
import os
import sys
import argparse
from os.path import isdir

from PDF.PDFMaker import PDFMaker as PDF
from Tools.Exceptions import WrongExtensionException


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--output', help='Output pdf file.')
    arg_parser.add_argument(
        '--encoding',
        help='Project or file encoding. Default: utf-8',
        default='utf-8'
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
        PDF(None, 'std', output, encoding, std=sys.stdin)
    else:
        if isdir(path):
            PDF(path, 'dir', output, encoding)
        else:
            _, extension = os.path.splitext(path)
            if extension in ['.cs', '.sln', '.csproj']:
                PDF(path, extension, output, encoding)
            else:
                raise WrongExtensionException


def test():
    PDF('/Users/aliser/Downloads/NSimulator', 'dir', 'test.txt', 'utf-8')


if __name__ == "__main__":
    # try:
    test()
    # main()
    # except Exception as e:
    #     print(str(e), file=sys.stderr)
    #     raise SystemExit(1)
