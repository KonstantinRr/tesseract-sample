#!/usr/bin/env python
import sys
from io import BytesIO

try:
    from PyPDF2 import PdfFileReader, PdfFileWriter
except ImportError:
    from pyPdf import PdfFileReader, PdfFileWriter

import pytesseract as pyt
from PIL import Image
from pdf2image import convert_from_bytes, convert_from_path
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)

def pdfConcat(input_files, output_stream):
    input_streams = []
    try:
        for input_file in input_files:
            input_streams.append(open(input_file, 'rb')
                if isinstance(input_file, str) else input_file)
        writer = PdfFileWriter()
        for reader in map(PdfFileReader, input_streams):
            for n in range(reader.getNumPages()):
                writer.addPage(reader.getPage(n))
        writer.write(output_stream)
    finally:
        for f in input_streams:
            f.close()

def convert(source, output):
    images = (convert_from_path(source) if isinstance(source, str) else
        convert_from_bytes(source.read()))
    
    pdfs = [pyt.image_to_pdf_or_hocr(image, extension='pdf', lang='nld') for image in images]
    pdfsIO = [BytesIO(pdf) for pdf in pdfs]

    if isinstance(output, str):
        with open(output, 'wb') as f:
            pdfConcat(pdfsIO, f)
    else:
        pdfConcat(pdfsIO, output)

if __name__ == '__main__':
    if sys.platform == 'win32':        # First open all the files, then produce the output file, and
        # finally close the input files. This is necessary because
        # the data isn't read from the input files until the write
        # operation. Thanks to
        # https://stackoverflow.com/questions/6773631/problem-with-closing-python-pypdf-writing-getting-a-valueerror-i-o-operation/6773733#6773733
        import os, msvcrt
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

    from pathlib import Path
    from os import listdir
    from os.path import isfile, join

    inputDir = 'input'
    outputDir = 'output'

    try:
        Path(inputDir).mkdir(parents=True, exist_ok=True)
        Path(outputDir).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f'Could not create input/output directories {e}')
        sys.exit(1)

    onlyfiles = [f for f in listdir('input') if isfile(join(inputDir, f))]
    for idx, i in enumerate(onlyfiles):
        print(f'Converting {idx}: {i}')
        convert(join(inputDir, i), join(outputDir, i))


    