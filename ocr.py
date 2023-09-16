from pytesseract import image_to_string, pytesseract
from cv2 import imread, cvtColor, COLOR_BGR2GRAY
from argparse import ArgumentParser
from platform import system
from csv import writer
from re import split
from glob import iglob
from os import path
from sys import exit


def print_verbose(basename, extracted):
    name_len = len(basename)
    print("+=" + ("=" * name_len) + "=+")
    print("| " + basename + " |")
    print("+=" + ("=" * name_len) + "=+")

    is_even = False
    for text in extracted:
        print(text)

        if is_even:
            print("-" * (len(text) + 2))

        is_even = not is_even

    print()


def process_img(pathname, writer, to_print):
    img = imread(pathname)
    final = cvtColor(img, COLOR_BGR2GRAY) # Grayscales the image

    ocr_text = image_to_string(final)
    extracted = split(r'\n\s*', ocr_text)
    basename = path.basename(pathname)
    writer.writerow([basename, extracted[0] + '\n' + extracted[1]])

    is_even = False
    buffer = ''

    for text in extracted[2:]:
        if not is_even:
            buffer += text
        else:
            writer.writerow(['', buffer + '\n' + text])
            buffer = ''

        is_even = not is_even

    if to_print:
        print_verbose(basename, extracted)


def main():
    parser = ArgumentParser(description = "Extract texts from images using Tesseract OCR")
    parser.add_argument('paths', metavar='P', nargs='+', help='paths of directories or files to process')
    parser.add_argument('-o', '--output', help='name of the output file')
    parser.add_argument('-v', '--verbose', action='store_true', help='print output to the terminal')

    args = parser.parse_args()
    valid_paths = []
    valid = False

    for path_arg in args.paths:
        abs_path = path.realpath(path_arg)

        if not path.exists(abs_path):
            print(f"{abs_path} does not exist!")
            continue
        
        valid = True
        valid_paths.append(abs_path)

    if not valid:
        print("OCR failed :<")
        exit(1)

    sup_exts = ['png', 'jpg', 'jpeg']
    output = args.output if args.output else 'output'

    with open(f'{output}.csv', 'w', newline='') as f:
        csv_writer = writer(f)

        for path_arg in valid_paths:
            if path.isdir(path_arg):
                for ext in sup_exts:
                    for file in iglob(f'{path_arg}/*.{ext}'):
                        process_img(file, csv_writer, args.verbose)
            else:
                process_img(path_arg, csv_writer, args.verbose)

    print("OCR complete!")


if __name__ == '__main__':
    if system() == 'Windows':
        pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

    main()

