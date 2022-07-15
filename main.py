import argparse
import traceback
import file_watchdog
from compiller import compile, HtmlpException
import htmlmin
from pathlib import Path


def main():
	args = parse_args()
	if not args.watch:
		try:
			compile_once(args)
			print("Succesfully compilled")
		except KeyboardInterrupt as e:
			return
		except HtmlpException as e:
			print(str(e))
	else:
		while(True):
			try:
				compile_once(args)
				print("Succesfully compilled")
			except KeyboardInterrupt as e:
				return
			except HtmlpException as e:
				print(str(e))

			file_watchdog.wait_modify(args.watch)

def parse_args():

	parser = argparse.ArgumentParser(description='Doing something')
	parser.add_argument('input_file', type=str, nargs=1,
						help='An input file')
	parser.add_argument('output_file', type=str, nargs='?', 
						default='output.html',
						help='An output file. Default is %(default)s')
	parser.add_argument('--watch', metavar='DIR',  action='store', nargs='?',
						default=False,
						help='Watch files in [DIR] and recompile when it`s files change. Default is current directory')
	parser.add_argument('--minify', action='store_true',
						help='Minifies output')
	parser.add_argument('--include-dir', metavar='DIR', type=str, action='store',
						default='./',
						help='Changes the include dir')
	args = parser.parse_args()
	if(args.watch == None):
		args.watch = './'
	return args



def compile_once(args):
	out = compile(args.input_file[0], args.include_dir, minify=args.minify)
	if args.minify:
		out = htmlmin.minify(out, remove_comments=True, remove_empty_space=True)
	with open(args.output_file, 'w') as file:
		file.write(out)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print()

