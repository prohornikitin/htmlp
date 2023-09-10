import argparse
from pathlib import Path
from typing import Optional, List, TextIO
import sys
from dataclasses import dataclass

@dataclass(frozen=True, kw_only=True)
class Args:
	out: TextIO
	input: List[Path]
	include_dir: Path
	need_minify: bool
	watch_dir: Optional[Path]


def parse_args() -> Args:
	parser = argparse.ArgumentParser(description='Doing something')
	parser.add_argument(
		'input_file', 
		type=str,
		nargs=1,
		help='An input file'
	)
	parser.add_argument(
		'--output-file',
		metavar='FILE',
		type=str,
		nargs='?',
		help='An output file'
	)
	parser.add_argument(
		'--watch',
		metavar='DIR',
		action='store',
		nargs='?',
		default=False,
		help='Watch files in [DIR] and recompile when it`s files change. Default is current directory'
	)
	parser.add_argument(
		'--minify',
		action='store_true',
		default=False,
		help='Minifies output'
	)
	parser.add_argument(
		'--include-dir',
		metavar='DIR',
		type=str,
		action='store',
		default='./',
		help='Changes the include dir'
	)
	args = parser.parse_args()

	if args.watch == False:
		watch = None
	elif args.watch == None:
		watch = Path('.')
	else:
		watch = Path(args.watch)

	if args.output_file == None:
		out = sys.stdout
	else:
		out = open(args.output_file, 'w')

	return Args(
		out = out,
		input = args.input_file,
		include_dir = Path(args.include_dir),
		need_minify = args.minify,
		watch_dir = watch
	)

