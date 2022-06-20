import argparse
import os
import time
import traceback

from compiller import compile
import htmlmin


def main():
    args = parse_args()
    if not args.watch:
        compile_once(args)
    else:
        while(True):
            try:
                compile_once(args)
                print("SUCCESS")
                wait_file_modified(args.input_file[0])
            except KeyboardInterrupt as e:
                raise e
            except:
                traceback.print_exc()

def parse_args():
    parser = argparse.ArgumentParser(description='Doing something')
    parser.add_argument('input_file', type=str, nargs=1,
                        help='an input file')
    parser.add_argument('output_file', type=str, nargs='?', 
                        default='output.html',
                        help='an input file')
    parser.add_argument('--watch', action='store_const',
                        const=True, default=False,
                        help='watch files and recompile when they change')
    parser.add_argument('--minify', action='store_const',
                        const=True, default=False,
                        help='minifies output')
    parser.add_argument('--include-dir', action='store',
                        default='./',
                        help='changes the include dir')
    return parser.parse_args()


def wait_file_modified(file_path):
    modified = modified_on = os.path.getmtime(file_path)
    while modified <= modified_on :
        time.sleep(0.5)
        modified = os.path.getmtime(file_path)


def compile_once(args):
    out = compile(args.input_file[0], args.include_dir)
    if args.minify:
        out = htmlmin.minify(out)
    with open(args.output_file, 'w') as file:
        file.write(out)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()